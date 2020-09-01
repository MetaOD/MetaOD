# implement the algorithm of delta debugging

# we first randomly put object images around other images
# until we find some issues.

# 
# then we start from there, and use delta debugging to proceed
# the cendroid of all the objects

from imagegym.env import ENV
import os
from PIL import Image

# background image 
bg = sys.argv[1]
# object image 
ob = sys.argv[2]
env = ENV(bg, ob, True)
im = Image.open(bg)
input_height, input_width = im.size
im = Image.open(ob)
obj_height, obj_width = im.size

import math

def collect_regions_of_objects(boxs):
    # return a list of boxes
    a = []
    for box in boxs:
        h = abs(box[0][1] - box[0][0])
        w = abs(box[1][1] - box[1][0])
        delta_box = math.sqrt(h ** 2 + w ** 2) / 2
        mid = (int(box[0][0] + h/2), int(box[1][0] + w/2))
        a.append((delta_box, mid))

    return a

def insert_object_images(x, y, idx):
    r = env.do_insert(x, y, idx)
    if r == "win":
        print ("win!!")
        return 1
    else:
        return 0

def insert_loc(boxs):
    # let's compute cendroid first.
    arr = []
    for box in boxs:
        h = abs(box[0][1] + box[0][0]) / 2.0
        w = abs(box[1][1] + box[1][0]) / 2.0
        arr.append((h, w))

    def centeroidnp(v, label):
        length = 0
        sum_x = 0
        sum_y = 0
        for v1 in v:
            if True:
                sum_x += v1[0]
                sum_y += v1[1]
                length += 1
        return int(sum_x/length), int(sum_y/length)

    return centeroidnp(arr, "")

base_delta_obj = math.sqrt(obj_height ** 2 + obj_width ** 2)


def delta_new_insertion(win, cl):
    # we need to move to XX.
    def average(x1, y1, x2, y2):
        return int((x1+x2)/2), int((y1+y2)/2)

    def close(mx, my, x1, y1):
        # compute the distance; 
        # if it is just too close, then terminate
        d = math.sqrt((x1-mx) ** 2 + (y1 - my) ** 2)
        return d < base_delta_obj / 6

    x0 = win[0]
    y0 = win[1]
    xc = cl[0]
    yc = cl[1]
    x2, y2 = xc, yc
    x1, y1 = x0, y0
    print ("start to delta debugging", x1, y1, x2, y2)
    idx = 0
    while True:
        idx += 1
        r = insert_object_images(x2, y2, idx)
        if r == 1:
            x1, y1 = x2, y2
            if close(mx, my, x1, y1):
                break
            x2, y2 = average(xc, yc, x1, y1)
        else:
            x2, y2 = average(x1, y1, x2, y2)
            if close(x1, y1, x2, y2):
                break

    return x1, y1


def delta_insertion(win, cl):
    # we need to move to XX.
    def average(x1, y1, x2, y2):
        return int((x1+x2)/2), int((y1+y2)/2)

    def close(mx, my, x1, y1):
        # compute the distance; 
        # if it is just too close, then terminate
        d = math.sqrt((x1-mx) ** 2 + (y1 - my) ** 2)
        return d < base_delta_obj / 6

    x1 = win[0]
    y1 = win[1]
    x2 = cl[0]
    y2 = cl[1]
    print ("start to delta debugging", x1, y1, x2, y2)
    max_x = x1
    max_y = y1
    idx = 0
    while True:
        idx += 1
        mx, my = average(x1, y1, x2, y2)
        print ("try new location", x1, y1, mx, my)
        if close(mx, my, x1, y1):
            break
        elif insert_object_images(mx, my, idx) == 1:
            max_x = mx
            max_y = my
            x1 = mx
            y1 = my
        else:
            x2 = mx
            y2 = my

    return max_x, max_y


from random import randint
def compute_insertion(a):
    base_delta_obj = math.sqrt(obj_height ** 2 + obj_width ** 2)

    obj_idx = randint(0, len(a)-1)
    print ("obj indx", obj_idx, a[obj_idx])
    d = base_delta_obj / 4 + a[obj_idx][0]
    x = a[obj_idx][1][0]
    y = a[obj_idx][1][1]
    # x' = x + (d * cos(a))
    # y' = y + (d * sin(a))
    # 30 * 12 = 360
    a = randint(1, 12) * 30
    print ("a ", a)
    x1 = x + d * math.cos(a)
    y1 = y + d * math.sin(a)

    return int(x1), int(y1)

def process():
    state = env.reset()
    a = collect_regions_of_objects(env.object_boxes)
    win_list = []
    bound = len(a) * 12
    # bound = 3
    while True:
        bound -= 1
        if bound == 0:
            break
        # let's do random insertion until find something
        x, y = compute_insertion(a)
        print ("try " + str(x) + " " + str(y))
        if insert_object_images(x, y, 0) == 1:
            # find one 
            win_list.append((x, y))
            break

    cl = insert_loc(env.object_boxes)

    for win in win_list:
        # mw = delta_insertion(win, cl)
        mw = delta_new_insertion(win, cl)
        print ("finish with : ", mw, win)

process()