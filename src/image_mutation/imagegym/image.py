# this file acts like the gym of OpenAL 
# to set up our environment, 
# we need one initial image and one object image 
# then it paste the object image over the background 
# with (x,y) provided by agent 

import numpy as np
import sys

def init(bg, ob):
    save_base_path(bg)
    save_object_path(ob)

def mutate(x, y, idx):
    # paste ob over bg and synthesize a new image 
    return insert_image(x, y, idx)

def save_base_path(bg):
    with open("./background_path.txt", 'w') as f:
        f.write(bg)

def save_object_path(ob):
    with open("./object_path.txt", 'w') as f:
        f.write(ob)

from PIL import Image, ImageOps

def object_image_path():
    with open("./object_path.txt", 'r') as f:
        l = f.readlines()[0]
    return l

def background_image_path():
    with open("./background_path.txt", 'r') as f:
        l = f.readlines()[0]
    return l

def synthesized_imagepath(idx):
    base = "./new_"
    path = base + str(idx) + ".png"
    return path

def insert_image(x, y, idx):
    obj_img = Image.open(object_image_path(), 'r')
    # obj_img.thumbnail(size, Image.ANTIALIAS)
    bg_img = Image.open(background_image_path())

    bg_img.paste(obj_img.convert('RGBA'), (x, y), mask=obj_img.convert('RGBA'))
    new_path = synthesized_imagepath(idx)
    bg_img.save(new_path)

    return new_path

