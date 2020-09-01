# 	1. Collect the locations of each object 
#	2. Find similar objects (identical labels) from the dataset and use that 
#	3. For all the images with the identical label:
#		a. Take this object
#		b. Compute a location to put the object (let's implement something simple)
#		c. All right, so since we have objects and locations, then put it back onto the original image.
#		d. Generate and store the new image into a subfolder

#!/usr/bin/python
import os

# let's assume before processing this case, we have already processed 
# all the images with semantics segmentation 

# result 
# step0 
# step1
# step2

from ast import literal_eval

# retrieve all the objects within one image and their locations
def get_all_objects_image(i):
    # results/step2/i 
    base = "./result/Step2_save_into_seperate/"
    i1 = i.split(".")[0]
    object_list = []
    path = base + i1 + "/object.log"
    if os.path.isfile(path) == False:
        # no object is extracted
        return []
    with open(path) as f:
        lines = f.readlines()

        for l in lines:
	    l = literal_eval(l)
            items = l
            # ('truck', 1, 269, 636, 5, 219)
	    # print items
            if (len(items) == 6):
                object_list.append((i, l[0], l[1], (int(l[2]), int(l[3]), int(l[4]), int(l[5]))))
            else:
                assert(len(items) == 7) # possible?
                object_list.append((i, l[0] + " " + l[1], l[2], (int(l[3]), int(l[4]), int(l[5]), int(l[6]))))

        return object_list 


def get_all_objects():
    lines = []
    with open("imagelist.txt") as f:
        lines = f.readlines()

    object_list_all = {}

    for l in lines[0:20]:
	l = l.strip()
        ol = get_all_objects_image(l)
        object_list_all[l] = ol

    return object_list_all 

def preprocess():
    ola = get_all_objects()

    return ola


def get_identical_objects(l, ola):
    # l: label defined in coco dataset
    res = []
    for key, value in ola.iteritems():
        for obj in value:
            label = obj[1]
            if l == label:
                res.append((key, obj))

    return res 

import numpy as np

def insert_loc(ola, i, obj):
    label = obj[1][1]
    v = ola[i]
    arr = []
    for v1 in v:
        loc = v1[3]
        # let's carry the label as well.
        arr.append((v1[1], (loc[0]+loc[1])/2.0, (loc[2]+loc[3])/2.0))
    #print arr

    # so we don't want to insert an overlapped image. 
    

    def centeroidnp(v, label):
        #length = len(v)
        #sum_x = np.sum(v[:, 0])
        #sum_y = np.sum(v[:, 1])
        length = 0
        sum_x = 0
        sum_y = 0
        for v1 in v:
            # if label == v1[0]:
            if True:
                sum_x += v1[1]
                sum_y += v1[2]
                length += 1
        return int(sum_x/length), int(sum_y/length)

    # FIXME 
    return centeroidnp(arr, label)


from PIL import Image, ImageOps

def insert_size(ola, i, obj):
    v = ola[i]
    arr = []
    for v1 in v:
        if v1[1] == obj[1][1]:
            # same label
            loc = v1[3]
            arr.append((abs(loc[0]-loc[1]), abs(loc[3]-loc[2])))
    sum_x = 0
    sum_y = 0
    for (t1, t2) in arr:
        sum_x += t1
        sum_y += t2
    sum_x = sum_x / len(arr)
    sum_y = sum_y / len(arr)

    return (sum_x, sum_y)

def object_image_path(obj):
    # image name 
    # object name
    # object id
    # print obj
    img_name = obj[1][0]
    obj_name = obj[1][1]
    obj_id = str(obj[1][2])
    base = "./result/Step2_save_into_seperate/"
    path = base + img_name + "/" + obj_name + "_" + obj_id + ".png"
    #print path
    return path

def image_path(i):
    base = "../../images/test2017/"
    path = base + i + ".jpg"
    return path

def insert_image(ola, i, obj, idx):
    size = insert_size(ola, i, obj) 
    loc = insert_loc(ola, i, obj)
    obj_img = Image.open(object_image_path(obj), 'r')
    obj_img.thumbnail(size, Image.ANTIALIAS)
    bg_img = Image.open(image_path(i))

    bg_img.paste(obj_img.convert('RGBA'), loc, mask=obj_img.convert('RGBA'))
    bg_img.save('./result/final/' + i + "_" + str(idx) + '.png')

def process(ola):
    lines = []
    with open("imagelist.txt") as f:
        lines = f.readlines()

    for l in lines[0:1]:
        i = l.strip()
        # if there is no object extracted from this image, then we don't go into the loop anyway
        t = 0
        idx = 0
        for item in ola[i]:
            t += 1
            r = get_identical_objects(item[1], ola)
            if len(r) > 0:
                # ok, we found one
                for r1 in r:
                    idx += 1
                    print "process ", i, "object", t, " mutation", idx
                    insert_image(ola, i, r1, idx)


if __name__ == "__main__":
    ola = preprocess()
    print ola
    # process(ola)



