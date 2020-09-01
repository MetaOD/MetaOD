import cv2, sys, os
import numpy as np

def compute_hisgram(path):
    hog = cv2.HOGDescriptor()
    im = cv2.imread(path)
    img_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    h = hog.compute(im)
    
    return h

def histogram_intersection(h1, h2):
    return cv2.compareHist(h1, h2, cv2.HISTCMP_INTERSECT)

def process_two_images(path1, path2):
    # print (path1, path2)
    h1 = compute_hisgram(path1)
    h2 = compute_hisgram(path2)

    h12 = histogram_intersection(h1, h2)

    # print (h12)
    # to normalize, we need to divide by the original image.
    r = (h12/np.sum(h2))
    print (path1, path2, r)
    return r

# process_two_images(sys.argv[1], sys.argv[2])

def iterate_images_for_one_background(base):
    os.system("ls " + base + " > t1")
    final = []
    start = []
    with open("t1") as f:
        lines = f.readlines()
        for l in lines:
            l = l.strip()
            if "obj_" in l or l.endswith(".png") == False:
                continue
            original_img = base.split(".png")[0] + ".png"
            base1 = "../../../../coco_test_2017/test2017/" + original_img
            if "final" in l:
                final.append(process_two_images(base + "/" + l.strip(), base1))
            else:
                start.append(process_two_images(base + "/" + l.strip(), base1))

        if len(final) != 0:
            af = sum(final)/len(final)
        else:
            af = None

        if len(start) != 0:
            ast = sum(start)/len(start)
        else:
            ast = None
        return (af, ast)


def iterate_background():
    final = []
    start = []
    with open("list") as f:
        lines = f.readlines()
        for l in lines:
            print (l)
            f, s = iterate_images_for_one_background(l.strip())
            if f != None:
                final.append(f)
            if s != None:
                start.append(s)
            # break

    if len(final) != 0:
        print (sum(final)/len(final))
    if len(start) != 0:
        print (sum(start)/len(start))
        

iterate_background()
