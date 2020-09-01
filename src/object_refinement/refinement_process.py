# do the object refinement
# including clustering
# and eliminating low quality clusters

# avaliable "policies" that can be selected for usage:
# 1. for an image of three persons and two dogs 
# 2. insert person and insert dog 
# 3. build a relation database (one single map)
#    person -> dog
#    dog    -> person
#    person -> bike
#    bike   -> person
#    ...
# 4. in that sense, we can also insert dog or bike, if that's an image of three persons
# 5. sort the object images and somehow pick the top qualities 

#from imagecluster import calc as ic
#from imagecluster import postproc as pp
import sys

# No use
def clustering(pool_path, cluster_path, label):
    ias = ic.image_arrays(pool_path, size=(224,224))
    model = ic.get_model()
    fps = ic.fingerprints(ias, model)
    
    fps = ic.pca(fps, n_components=0.95)
    clusters = ic.cluster(fps, sim=0.5)
    pp.make_links(clusters, cluster_path + '/' + label)


import os
def small_images_remover(base):
    # just iterate every pool of objects and remove low quality 
    # just sort by size and shave small images.
    def size(l):
        return os.path.getsize(l)
    obj_list = {}
    for path, _, files in os.walk(base):
        for name in files:
            label = name.split("_")[0]
            l = os.path.join(path, name)
            if label in obj_list:
                obj_list[label].append((l, size(l)))
            else:
                obj_list[label] = [(l, size(l))]
    
    P = 0.9
    # 2019-07-15
    # seems that we will need to increase the number from 0.7 -->　0.9
    # we remove 90% of object instances 
    for _, v in obj_list.items():
        if (len(v) < 6):
            continue
        else:
            v.sort(key=lambda n: n[1]) 
            n = int(len(v) * P)
            for i in range(n):
                os.system("mv " + v[i][0] + " " + v[i][0]+"_drop")
 

import itertools

# let's build a database for task 3
def build_db(base):
    m = {}
    for path, subdirs, files in os.walk(base):
        for name in files:
            if "object.log" in name:
                l = os.path.join(path, name)
                with open(l) as f:
                    lines = f.readlines()
                    nl = []
                    for l in lines:
                        n = l.split(',')[0][2:-1]
                        if " " in n:
                            n = n.replace(" ", "-")
                        nl.append(n)
                    for i, j in itertools.product(nl, nl):
                        if i != j:
                            m[i] = j
    return m


def build_object_hashdb(base):
    hash_m = {}
    for path, subdirs, files in os.walk(base):
        for name in files:
            if ".png" in name:
                l = os.path.join(path, name)
                hash_m[name] = compute_image_hash(l)
    # print (hash_m)
    return hash_m


from PIL import Image
import imagehash

def compute_image_hash(i):
    hash = imagehash.average_hash(Image.open(i))
    return hash

import os, random
# randomly select one from top ten high quality images?
def one_from_top_N(label, image):
    # pick top ten good images from a pool? How to?
    # check whether it has over ten files 
    N = 10
    t = [name for name in os.listdir(base_object + label + "/") if name.endswith(".png")]
    n = len(t)
    if n > N:
        files = []
        for i in range(N):
            files.append(random.choice(os.listdir(base_object + label + "/")))
        return random.sample(files, 1)
    else:
        return random.sample(t, 1)


def hamming(a, b):
    return bin(a^b).count('1')

def one_with_close_hash(label, image):
    # select one image with the closest hash value of objects of the same label on the image 
    iid = image.split(".")[0]
    average_hash = []
    label_hash = {}
    for k, v in hash_m.items():
        # print (k, v, iid, label)
        if iid in k and label in k:
            average_hash.append(v)
        if label in k and k.endswith(".png"):
            # note that for this, we put every possible 
            # object instances, including the original objects into the set, 
            # AS LONG AS it is large enough.
            label_hash[k] = v
    a1 = []
    if len(average_hash) == 0:
        # this is possible, suppose we decide to insert a dog for a image of only human beings 
        # just randomly select one 
        return random.choice(list(label_hash.keys()))
    else:
        for a in average_hash:
            # print ("hash value", a)
            a1.append(int(str(a), 16))
        ah = int(sum(a1) / len(average_hash))
        min_distance = 999999
        min_label = None
        for k, v in label_hash.items():
            # print ("check other hash", v)
            distance = hamming(int(str(v), 16), ah)
            if distance < min_distance:
                # print ("find one minimal ", v, distance, ah)
                min_distance = distance
                min_label = k
        assert min_label 

        return min_label


base_image = ""
base_object = ""
m = {}
hash_m = {}
def init(i, o):
    global m
    global hash_m
    global base_image
    global base_object
    base_image = o
    base_object = i
    # base = "../image_pool/"
    # FIXME
    # small_images_remover(base_object)
    m = build_db(base_image)
    hash_m = build_object_hashdb(base_object)
    # print m

def get_labels(image):
    with open(base_image + image.split(".")[0] + "/object.log") as f:
        lines = f.readlines()
        nl = []
        for n in lines:
            n1 = n.split(',')[0][2:-1]
            n1 = n1.replace(" ", "-")
            nl.append(n1)
        s = set(nl)
        ss = set()
        for s1 in s:
            if s1 in m:
                # note that this is possible such that m does not have s1 as a key
                # for instance, an image contains objects of the same label
                t = m[s1]
                if t not in s:
                    ss.add(t)

    # nl: a list of all the objects in the image 
    # s1: a set of corelated object labels 
    return (nl, ss)

# the input is an image 
# output: a set of objects used for insertion.
# note that given an image of N objects
# we will need to iterate for 10 * N synthetic images 
# in that sense, we shouldn't generate too many object files for each object.
# maybe it's like this:
# suppose we have N objects in the input image,
# then we prepare N objects as well for use.
import random
def process(image):
    # clustering("../object_pool/" + label, "../object_clusters/" + label, label)
    (nl, s1) = get_labels(image)
    N = len(nl)
    print (nl, s1)
    # then let's prepare N labels as well
    # candidates = random.sample(nl + list(s1), N)
    # FIXME
    # so that might give us a easier time, considering that 
    # we can find object instances of identical label in the background image.
    candidates = random.sample(nl, N)
    # In that sense, for an image of N objects, we randomly select N objects close to existing cases for the usage.
    res = []
    for cl in candidates:
        # res.append(one_from_top_N(cl, image))
        res.append(one_with_close_hash(cl, image))
    return res
