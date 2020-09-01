# move images out of the folder 

# labels for clustering 

from os import walk

import os
import sys

def build_folder(base, labels):
    for label in labels:
        os.system("mkdir -p " + base + "/" + label)


def label_collector(base):
    s = set()
    for (dirpath, dirnames, filenames) in walk(base):
        image_name = dirpath.split("/")[-1]
        for fn in filenames:
            if ".png" in fn:
                # wine_cup_1.png
                t = fn.split("_")[:-1]
                label = "_".join(t)
                if " " in label:
                    label = label.replace(" ", "-")
                    os.system("mv " + dirpath + "/" + fn.replace(" ", "\ ") + " " + dirpath + "/" + fn.replace(" ", "-"))
                s.add(label)
    return s

def build_pool(base, pooldir):
    labels = label_collector(base)
    build_folder(pooldir, labels)

    f = []
    print (labels)
    for label in labels:
        for (dirpath, dirnames, filenames) in walk(base):
            image_name = dirpath.split("/")[-1]
            for fn in filenames:
                if label in fn:
                    idx = fn.split("_")[-1].split(".")[0]
                    newname = label + "_" + image_name + "_" + idx + ".png"
                    os.system("cp " + dirpath + "/" + fn + " " + pooldir + "/" + label + "/" + newname)


if __name__ == "__main__":
    build_pool(sys.argv[1], sys.argv[2])
