# this is the whole workflow
# three modules 

import os


class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def process_object_extraction(images):
    # extract objects and save into pools 
    # let's randomly select N 
    # images from the COCO pool
    with cd("../object_extraction/"):
        for i in images:
            os.system("python image_disection.py " + i)

        # then we setup the pool structure for the second step 
        os.system("python image_cluster.py result/Step2_save_into_seperate/ result/pool/")

        os.system("mv result/pool/* ../object_pool/")
        os.system("mv result/Step2_save_into_seperate/* ../image_pool/")

import sys
sys.path.append('../')
import object_refinement.refinement_process as RP

def init_object_refinement():
    # refinement; clustering and so on
    # basically even if we skip this one, we still can 
    # proceed the following steps, right?
    target_dir = "../object_pool/"
    image_dir = "../image_pool/"
    RP.init(target_dir, image_dir)

def process_object_refinement(i):
    return RP.process(i)


from os import walk

def get_obj_list(obj_name, i, c):
    print (obj_name, i, c)
    # the baseline approach is to extract all the objects with 
    # the same label, after the clustering with set of the same label
    # ../obj_pool/label/
    obj_name = obj_name.replace(" ", "-")
    with cd("../object_pool/" + obj_name):
        # ideally, we have several clusters right here, 
        # and we try all objects within the same cluster with obj_name

        # 1. find the object within a cluster 
        r = None
        for (dirpath, dirnames, filenames) in walk("."):
            for f in filenames:
                if (i + "_" + str(c)) in f:
                    # OK, we are in the right cluster
                    target_dir = dirpath
                    r = os.listdir(target_dir)
                    break
        assert r
        return r

import os.path

def resize(label, lines):
    c = 0
    xs = 0
    ys = 0
    for l in lines:
        if label.replace("-", " ") in l:
            items = l.strip().split(",")
            x1 = int(items[2])
            x2 = int(items[3])
            y1 = int(items[4])
            y2 = int(items[5][:-1])
            xs += abs(x2-x1)
            ys += abs(y2-y1)
            c += 1
 
    if (c == 0):
        # just take the average
        return resize("", lines)
    else:
        return (int(xs/c), int(ys/c))


def process_object_insertion(i, objects):
    # insert objects into the image, and also 
    # do a delta debugging style augmentation
    with cd("../image_mutation"):
        i1 = i.split(".")[0]
        # let's first select one image 
        # image_pool/ + i + 
        p = "../image_pool/" + i1 + "/object.log"
        if os.path.isfile(p) == False:
            # well maybe it is because no object is detected.
            print ("[LOG] NO OBJECT IS DETECTED")
            return 

        lines = []
        with open(p) as f:
            lines = f.readlines()
        c = 1
        for o in objects:
            label = o.split("_")[0]
            x, y = resize(label, lines)
            os.system("python3 image_insertion.py " + i.strip() + " " + o + " " + str(x) + " " + str(y) + " " + str(c))
            c += 1
            #break


def clean():
    os.system("rm -rf ../object_extraction/result/*")
    os.system("rm -rf ../image_pool/")
    os.system("rm -rf ../object_pool/")
    os.system("mkdir ../image_pool/")
    os.system("mkdir ../object_pool/")
    os.system("mkdir ../object_extraction/result/Step0_object_detection")
    os.system("mkdir ../object_extraction/result/Step1_extract_object")
    os.system("mkdir ../object_extraction/result/Step2_save_into_seperate")
    os.system("mkdir ../object_extraction/result/pool")

import os.path
def valid_image(i):
    # ../image_pool/000000313994/obj
    i1 = i.split(".")[0]
    return os.path.isfile("../image_pool/" + i1 + "/object.log") 

def process():
    clean()
    # the image list contains randomly selected N images 
    # from the COCO test 2017 data set 
    with open("imagelist.txt") as f:
        images = f.readlines()

    process_object_extraction(images)
    return

    init_object_refinement()
    for i in images:
        if valid_image(i) == False:
            continue
        objects = process_object_refinement(i)
        print (objects)
    #     # why set? because there can exist redundant labels
        process_object_insertion(i, set(objects))
    #     # break

process()
