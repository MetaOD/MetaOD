# the empirical evidence we would like to show for the evaluation.

from imagegym.env import ENV
import os
from PIL import Image


import math



def collect_regions_of_objects(boxs):
    # return a list of boxes
    a = []
    for box in boxs:
        w = abs(box[0][1] - box[0][0])
        h = abs(box[1][1] - box[1][0])
        delta_box = math.sqrt(h ** 2 + w ** 2) / 2
        mid = (int(box[0][0] + w/2), int(box[1][0] + h/2))
        a.append((delta_box, mid, w, h))

    #print (boxs)
    #print (a)
    return a

def insert_object_images(x, y, idx):
    r = env.do_insert(x, y, idx)
    if r == "win":
        print ("win!!")
        return 1
    else:
        return 0
        # return 1

from random import randint
def compute_insertion(arr):
    def aux():
        base_delta_obj = math.sqrt(obj_height ** 2 + obj_width ** 2)

        obj_idx = randint(0, len(arr)-1)
        # 10% distance
        d = (base_delta_obj / 2 * 1.1) + arr[obj_idx][0] / 2
        x = arr[obj_idx][1][0]
        y = arr[obj_idx][1][1]
        # x' = x + (d * cos(a))
        # y' = y + (d * sin(a))
        # 30 * 12 = 360
        a = randint(1, 12) * 30
        x1 = x + d * math.cos(a)
        y1 = y + d * math.sin(a)

        #print ("try ", base_delta_obj, obj_idx, x1, y1)
        return int(x1), int(y1)
    c = 0 
    while True:
        x1, y1 = aux()
        r1 = env.check_overlapping(x1, y1, "")
        r2 = env.check_boundary(x1, y1)
        c += 1
        if c == 20:
            return None
        if r1 == False and r2 == True:
            return x1, y1
        else:
            print ("bad insertion", r1, r2)
            # return x1, y1
            continue


def random_insertion(arr):
    def aux():
        # input_height, input_width = im.size
        x = randint(int(obj_height/2), input_height - int(obj_height/2))
        y = randint(int(input_width/2), input_width - int(obj_width/2))
        return x, y
    c = 0
    while True:
        x1, y1 = aux()
        c += 1
        r1 = env.check_overlapping(x1, y1, "")
        r2 = env.check_boundary(x1, y1)
        if c == 20:
            return None
        if r1 == False and r2 == True:
            return x1, y1
        else:
            print ("bad insertion", r1, r2)
            continue

# x1 = target_obj_x + 2 * 0.5 * inserted_obj_x
# y1 = target_obj_y + 2 * 0.5 * inserted_obj_y
# x2 = target_obj_x + 2 * inserted_obj_x
# y2 = target_obj_y + 2 * inserted_obj_y
def guided_new_insertion(arr):
    def compute_distance(target_obj_x, target_obj_y, inserted_obj_x, inserted_obj_y):
        x1 = target_obj_x + inserted_obj_x
        y1 = target_obj_y + inserted_obj_y
        x2 = target_obj_x + 2 * inserted_obj_x
        y2 = target_obj_y + 2 * inserted_obj_y
        #print ("compute distance", x1, y1, x2, y2)
        return (x1, y1, x2, y2)

    def sampling(x1, y1, x2, y2):
        x = 0.0
        y = 0.0
        while(x == 0.0 and y == 0.0):
            x = random.uniform(0, 1) * x2
            y = random.uniform(0, 1) * y2

        if(x < x1 and y < y1):
            xpower = math.ceil((math.log(x1) - math.log(x)) / math.log(x2/x1))
            ypower = math.ceil((math.log(y1) - math.log(y)) / math.log(y2/y1))
            power = min(xpower, ypower)
            x *= math.pow(x2 / x1, power)
            y *= math.pow(y2 / y1, power)

        r = randint(0, 4)
        if((r & 1) != 0):
            x = -x
        if((r & 2) != 0):
            y = -y

        return (int(x), int(y))

    def aux():
      obj_idx = randint(0, len(arr)-1)
      x = arr[obj_idx][2]
      y = arr[obj_idx][3]

      t = compute_distance(x, y, obj_width, obj_height)
      #print ("what we want", t, obj_width, obj_height)

      x, y = sampling(t[0]/2, t[1]/2, t[2]/2, t[3]/2)
      #print ("random number", x, y)
      # compensate 
      x1 = x + arr[obj_idx][1][0]
      y1 = y + arr[obj_idx][1][1]
      #print ("random coordinator", x1, y1)
      return (x1, y1)

    c = 0
    while True:
      x1, y1 = aux()
      r1 = env.check_overlapping(x1, y1, "")
      r2 = env.check_boundary(x1, y1)
      c += 1
      if c == 20:
        return None
      if r1 == False and r2 == True:
        # all set
        return x1, y1
      else:
        print ("bad insertion", r1, r2)
        continue
        # return x1, y1

import random
import math

def new_guided_insertion(arr):
    def distance(alpha, x, y):
        c = math.cos(alpha)
        s = math.sin(alpha)
        r1 = x/(abs(c))
        r2 = y/(abs(s))
        return min(r1, r2)

    def aux():
        base_delta_obj = math.sqrt(obj_height ** 2 + obj_width ** 2)

        obj_idx = randint(0, len(arr)-1)
        x = arr[obj_idx][1][0]
        y = arr[obj_idx][1][1]
        # r = (base_delta_obj / 2) + arr[obj_idx][0] / 2
        r = (base_delta_obj) + arr[obj_idx][0]

        # random angle
        alpha = 2 * math.pi * random.random()
        r0 = distance(alpha, arr[obj_idx][2], arr[obj_idx][3])
        # r1 ~ 1
        r1 = r0 / float(r)
        print ("percentage", r1)

        # random radius
        r1 = r * random.uniform(r1, 1)
        # calculating coordinates
        x1 = r1 * math.cos(alpha) + x
        y1 = r1 * math.sin(alpha) + y
        
        print ("try ", base_delta_obj, obj_idx, x1, y1)
        return int(x1), int(y1)

    c = 0
    while True:
        x1, y1 = aux()
        r1 = env.check_overlapping(x1, y1, "")
        r2 = env.check_boundary(x1, y1)
        c += 1
        if c == 20:
            return None
        if r1 == False and r2 == True:
            # all set
            return x1, y1
        else:
            print ("bad insertion", r1, r2)
            continue
            # return x1, y1

def process(i):
    state = env.reset()
    a = collect_regions_of_objects(env.object_boxes)
    win_list = []
    # bound = len(a) * 12
    # yes, let's do this!
    bound = len(a) * 12
    # bound = 3
    c = 1
    if bound == 0:
        # too bad
        return
    print ("START TO PROCESS", bound)
    while True:
        bound -= 1
        if bound == 0:
            break
        # let's do guided insertion until find something
        # x, y = compute_insertion(a)
        # t = compute_insertion(a)
        # new guided method
        # t = new_guided_insertion(a)
        # let's do random insertion until find something
        # x, y = random_insertion(a)
        # t = random_insertion(a)
        # x, y = random_insertion(a)
        t = guided_new_insertion(a)
        if t == None:
            # we spent too many times but just cannot find a good position to insert
            print ("waste one time of check")
            continue
        else:
            x, y = t

        print ("try " + str(x) + " " + str(y))
        if insert_object_images(x, y, 0) == 1:
            # find one
            os.system("cp new_0.png new_" + str(i) + "__" + str(c) + ".png" )
            c += 1
            win_list.append((x, y))

    print ("WINLIST", len(win_list))
    # for w in win_list:
    #     print (w)

bg = ""
ob = ""
env = None
im = None
input_height = None
input_width = None
obj_height = None
obj_width = None


def main():
    global bg
    global ob
    global env
    global im
    global input_height
    global input_width
    global obj_height
    global obj_width

    #N = 50
    lines = []
    #with open("coco_list") as f:
    #    lines = f.readlines()
    with open("preliminary_study_random_selected_image_list") as f:
        lines = f.readlines()
    # for i in range(N):
    for i in range(len(lines)):
        #obj_idx = randint(0, len(lines)-1)
        obj_idx = i
        n = lines[obj_idx]
        bg = "../../../../coco_test_2017/test2017/" + n.strip()

        # randomly select 50 images from the coco set
        # bg = "../../data/kite.png"
        ob = "../../data/bird.png"
        print ("random test image: ", n)
        env = ENV(bg, ob, True)
        im = Image.open(bg)
        input_height, input_width = im.size
        im = Image.open(ob)
        obj_height, obj_width = im.size
        process(i)

main()


