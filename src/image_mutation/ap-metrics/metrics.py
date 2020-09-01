# let's calculate regarding AP metrics and whether labels are consistent


# input: the ground truth file and detection file.

# python pascalvoc.py -gt ./test_gt  -det ./test_dt
import os

# prepare the data

# os.system("mv gt.txt ./test_gt/0001.txt")
# os.system("mv dt.txt ./test_dt/0001.txt")

os.system("python3 ap-metrics/pascalvoc.py -gt ./test_gt  -det ./test_dt > log.txt")

# analyze the outputs 
with open("log.txt") as f:
    lines = f.readlines()

type_one_failure = False
type_two_failure = False

for l in lines:
    if "AP:" in l and "mAP" not in l:
        if "nan%" in l:
            # all right, we have extra label issues 
            type_one_failure = True
        elif "100.00%" not in l:
            type_two_failure = True

print (type_one_failure, type_two_failure)
