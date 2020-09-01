# this is the env interface.
import imagegym.env_google_vision_api as EG
import imagegym.env_amazon_api as EA
import imagegym.env_ibm_api as EI
import imagegym.env_microsoft_api as MA
# import env_amazon_api as EA
import imagegym.image as I
# import image as I
import logging
import numpy as np
from skimage import io
import os

from PIL import Image
from google.cloud import vision


CELL_EMPTY = 0.0
CELL_OCCUPIED = 1.0
CELL_CURRENT = 2.0

# Actions
LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3
actions_dict = {
    LEFT:  'left',
    UP:    'up',
    RIGHT: 'right',
    DOWN:  'down',
}

import paramiko

class ENV(object):
    """
    the env class, encapsulate the image and web service interface.
    """
    def __init__(self, bg, ob, use_raw_pixel, agent=(0,0), target=None):
        self.num_actions = len(actions_dict)
        self.bg = bg
        self.ob = ob
        self.use_raw_pixel = use_raw_pixel
        I.init(bg, ob)
        # FIXME only for Google AutoML
        # https://github.com/googleapis/google-cloud-python/issues/7381
        # self.client = vision.ImageAnnotatorClient()
        self.init_configs()
        self.reset()

        # ip='35.205.237.172'
        # port=22
        # username='XXX'
        # password='XXX'

        # self.ssh = paramiko.SSHClient()
        # self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # self.ssh.connect(ip,port,username,password)

    def reset(self):
        # bottom left corner
        # agent = (int(self.obj_nrows/2), self.ncols - int(self.obj_ncols))
        # top left corner
        # agent = (int(self.obj_nrows/2), int(self.obj_ncols/2))
        # bottom right corner
        # agent = (self.nrows - int(self.obj_nrows), self.ncols - int(self.obj_ncols))
        # top right corner
        agent = (self.nrows - int(self.obj_nrows), int(self.obj_ncols))
        self.agent = agent
        self.maze = np.copy(self._maze)
        nrows, ncols = self.maze.shape
        row, col = agent
        self.maze[row, col] = CELL_CURRENT
        self.visited = set()
        self.state = ((row, col), 'start')
        self.total_reward = 0
        self.min_reward = -0.5 * self.maze.size
        self.reward = {
            'blocked':  self.min_reward,
            'invalid': -0.75,
            'valid':   -0.05,
            'visited': -0.25,
            # 'invalid': -15.0/self.maze.size,
            # 'valid':   -1.0/self.maze.size,
            # 'visited': -5.0/self.maze.size,
            'win': 2.0
        }
        self.is_win = False

        return self.init_observe()

    def init_observe(self):
        if self.use_raw_pixel == True:
            im = io.imread(self.bg)
            return im
        else:
            return np.array([[*(self.agent[0], self.agent[1])]])

    def init_configs(self):
        # let's use the background image to query the server
        # and update the box
        self.object_boxes = []
        self.label0 = []
        self.confidences = []
        # res = EI.localize_objects(self.client, self.bg)
        res = EA.localize_objects(self.bg)
        # res is the ground truth
        # 2019-06-22 let's store the ground truth
        with open("0001.txt", 'w') as f:
            for r in res:
                f.write(r[0] + " " + " " + str(r[2][0][0]) + " " + str(r[2][0][1]) + " " + str(r[2][1][0]) + " " + str(r[2][1][1]) + "\n")
        os.system("mv 0001.txt ap-metrics/test_gt/")

        for r in res:
            self.object_boxes.append(r[2])
            self.confidences.append(r[1])
            self.label0.append(r[0])

        # let's add a new label though
        # self.label0.append("Person")
        im = Image.open(self.bg)
        self.nrows, self.ncols = im.size

        im = Image.open(self.ob)
        self.obj_nrows, self.obj_ncols = im.size

        self._maze = np.full((self.nrows, self.ncols), CELL_EMPTY)
        self._maze[0][0] = CELL_CURRENT

        def check_box(i, j):
            for o in self.object_boxes:
                if i >= o[0][0] and i <= o[0][1] and j >= o[1][0] and j <= o[1][1]:
                    return True
            return False

        # then update the "maze" with these boxes as forbidden areas
        for i in range(len(self._maze)):
            for j in range(len(self._maze[0])):
                if check_box(i, j):
                    self._maze[i][j] = CELL_OCCUPIED

        image = Image.open(self.ob)
        self.step_x, self.step_y = image.size
        self.step_x = int(self.step_x / 2)
        self.step_y = int(self.step_y / 2)
        self.cache = {}

    def compute_reward_by_confidence(self, res):
        # let's tentatively take all the confidence as the reward
        t = 0.0
        for r in res:
            t += r[1]
        # the higher the confidence is, the lower the reward is
        return 1 / t

    def compute_terminate(self, res):
        label = [x[0] for x in res]
        label.sort()
        self.label0.sort()
        # also shouldn't overlapping
        c = label.count("Person")
        c1 = self.label0.count("Person")
        # return self.label0 != label
        print ("person", c, c1)
        c1 = c != c1

        c = label.count("Bird")
        c0 = self.label0.count("Bird")
        print ("bird", c, c0)
        c2 = abs(c - c0) > 1

        c1 = c1 or c2

        # get mode; let's make sure this is valid
        (nrow, ncol), nmode = agent, mode = self.state
        c2 = mode == "valid"
        print (c1, c2)
        # FIXME
        # return c1 and c2
        return c1

    def compute_terminate_new(self, x, y, res):
# compute upper left corner coordinate and therefore rule out inserted object
        x0 = int(x - self.obj_nrows/2)
        y0 = int(y - self.obj_ncols/2)

        al = []
        for r in res:
            x1 = r[2][0][0]
            y1 = r[2][1][0]
            x2 = r[2][0][1]
            y2 = r[2][1][1]
            xc = (x1 + x2) / 2
            yc = (y1 + y2) / 2
            if abs(x1 - x0) < 10 and abs(y1 - y0) < 10:
                # the inserted object so we remove it
                print ("REMOVE")
                continue
            elif self.check_overlapping_inserted_box(xc, yc, x, y):
                # if the XXX is within the box.
                print ("REMOVE 2")
                continue

            else:
                al.append(r)

        res = al

        if len(res) != 0:
            with open("0001.txt", 'w') as f:
                for r in res:
                    f.write(r[0] + " " + str(r[1]/100)[0:3] + " " + str(r[2][0][0]) + " " + str(r[2][0][1]) + " " + str(r[2][1][0]) + " " + str(r[2][1][1]) + "\n")
            os.system("mv 0001.txt ap-metrics/test_dt/")

            os.system("python3 ap-metrics/metrics.py > ap_log.txt")
            with open("ap_log.txt") as f:
                lines = f.readlines()

            # print (x, y)

            if "True" in lines[-1]:
                return True
            else:
                return False
        else:
            # must be an issue
            return True

    def act(self, action, idx):
        self.update_state(action)
        reward = self.get_reward(idx)
        self.total_reward += reward
        status = self.game_status()
        env_state = self.observe()
        logging.warning("action: {:d} | reward: {: .2f} | status: {}".format(action,reward,status))

        return env_state, reward, status

    def observe(self):
        if self.use_raw_pixel:
            im = io.imread(self.new_path)
            return im
        else:
            return np.array([[*(self.agent[0], self.agent[1])]])

    def update_state(self, action):
        (nrow, ncol), nmode = agent, mode = self.state

        valid_actions = self.valid_actions()

        if not valid_actions:
            nmode = 'blocked'
        elif action in valid_actions:
            nmode = 'valid'
            if action == LEFT:
                nrow -= self.step_x
            elif action == UP:
                ncol -= self.step_y
            elif action == RIGHT:
                nrow += self.step_x
            elif action == DOWN:
                ncol += self.step_y
        else:
            nmode = 'invalid'

        self.agent = (nrow, ncol)
        self.state = (self.agent, nmode)

    def cache_insertion_results(self, x, y):
        # well, if there already exists a result, then we don't need
        # to do that.
        if ((x, y) in self.cache):
            return self.cache[(x, y)]
        else:
            return None

    def update_cache(self, x, y, res):
        self.cache[(x, y)] = res

    def get_reward(self, idx):
        agent, mode = self.state
        x, y = agent

        # first create a new image
        res0 = self.cache_insertion_results(x, y)
        if res0 == None:
            self.new_path = I.mutate(int(x - self.obj_nrows/2), int(y - self.obj_ncols/2), idx)
            # then compute the reward
            # res = EG.localize_objects(self.new_path)
            # res = EG.localize_objects(self.client, self.new_path)
            res = EA.localize_objects(self.new_path)
            # print (res)
            self.update_cache(x, y, res)
        else:
            self.new_path = I.mutate(int(x-self.obj_nrows/2), int(y - self.obj_ncols/2), idx)
            res = res0

        if (len(res) == 0) or self.compute_terminate(res) == True:
            self.is_win = True
            return self.reward['win']
        elif agent in self.visited:
            # penalty for returning to a cell which was visited earlier
            return self.reward['visited']
        elif mode == 'invalid':
            return self.reward['invalid']
        elif mode == 'valid':
            self.visited.add(agent)
            return self.reward['valid']
        elif mode == 'blocked':
            # let's hope this won't happen
            # FIXME
            return self.reward['blocked']

    def valid_actions(self):
        (row, col), mode = self.state
        actions = [LEFT, UP, RIGHT, DOWN]
        nrows, ncols = self.maze.shape

        if col - 2.0 * self.step_y <= 0:
            actions.remove(UP)
        if col + 2.0 * self.step_y >= ncols-1:
            actions.remove(DOWN)
        if row - 2.0 * self.step_x <= 0:
            actions.remove(LEFT)
        if row + 2.0 * self.step_x >= nrows-1:
            actions.remove(RIGHT)

        if row-self.step_x > 0 and self.check_overlapping(row-self.step_x,col, "left"):
            actions.remove(LEFT)
        if row+self.step_x < ncols-1 and self.check_overlapping(row+self.step_x,col, "right"):
            actions.remove(RIGHT)

        if col-self.step_y > 0 and self.check_overlapping(row,col-self.step_y, "up"):
            actions.remove(UP)
        if col+self.step_y < ncols-1 and self.check_overlapping(row,col+self.step_y, "down"):
            actions.remove(DOWN)

        return actions

    def check_overlapping(self, row, col, a):
        def overlapping1D(box1,box2):
            return box1[1] >= box2[0] and box2[1] >= box1[0]
        def overlapping2D(box1,box2):
            return overlapping1D(box1[0], box2[0]) and overlapping1D(box1[1], box2[1])

        # let's first compute the box of the object file
        # let's define a grey zone here. 
        # obj_norws / 8; 
        #box_row = (int(row - self.obj_nrows/2 - self.obj_nrows/8), int(row + self.obj_nrows/2 + self.obj_nrows/8))
        #box_col = (int(col - self.obj_ncols/2 - self.obj_ncols/8), int(col + self.obj_ncols/2 + self.obj_ncols/8))
        box_row = (int(row - self.obj_nrows/2), int(row + self.obj_nrows/2))
        box_col = (int(col - self.obj_ncols/2), int(col + self.obj_ncols/2))
        box0 = (box_row, box_col)
        for box in self.object_boxes:
            if overlapping2D(box0, box):
                return True
        return False


    def check_overlapping_inserted_box(self, row, col, x0, y0):
        box_row = (int(x0 - self.obj_nrows/2), int(x0 + self.obj_nrows/2))
        box_col = (int(y0 - self.obj_ncols/2), int(y0 + self.obj_ncols/2))
        # so just want to make sure the object is not within the 
        # bounding box of the inserted object
        if row >= box_row[0] and row <= box_row[1] and col >= box_col[0] and col <= box_col[1]:
            return True
        return False
    

    def check_boundary(self, row, col):
        x1 = row - self.obj_nrows/2
        x2 = row + self.obj_nrows/2
        y1 = col - self.obj_ncols/2
        y2 = col + self.obj_ncols/2

        # -23.0 27.0 640 -21.5 25.5 428
        print (x1, x2, self.nrows, y1, y2, self.ncols)
        return x1 > 0 and x2 < self.nrows and y1 > 0 and y2 < self.ncols

    def game_status(self):
        if self.total_reward < self.min_reward:
            # is it correct?
            return "lose"
        elif self.is_win == True:
            return "win"
        else:
            return "playing"

    def rendering(self):
        image = Image.open(self.new_path)
        image.show()


    def do_insert(self, x, y, idx):
        res0 = self.cache_insertion_results(x, y)
        if res0 == None:
            self.new_path = I.mutate(int(x-self.obj_nrows/2), int(y-self.obj_ncols/2), idx)
            # res = EG.localize_objects(self.new_path)
            # res = EG.localize_objects(self.client, self.new_path)
            res = EA.localize_objects(self.new_path)
            print (res)
            self.update_cache(x, y, res)
        else:
            self.new_path = I.mutate(int(x-self.obj_nrows/2), int(y-self.obj_ncols/2), idx)
            res = res0

        if (len(res) == 0) or self.compute_terminate_new(x, y, res) == True:
            return "win"
        else:
            return "lose"


from random import randint

if __name__ == "__main__":
    bg = "../../../data/kite.jpg"
    ob = "../../../data/person.png"

    env = ENV(bg, ob)

    for i in range(1):
        state = env.reset()
        print (env.act(RIGHT, 1))
        print (env.act(DOWN, 2))
        print (env.act(DOWN, 3))
        print (env.act(DOWN, 4))
        print (env.act(DOWN, 5))
        print (env.act(DOWN, 6))
        print (env.act(DOWN, 7))
        print (env.act(DOWN, 8))
        print (env.act(DOWN, 9))
        print (env.act(DOWN, 10))
        print (env.act(DOWN, 11))
