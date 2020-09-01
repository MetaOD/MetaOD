import os 
import sys

# python3 Step0_object_detection.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/dog.jpg # python3 Step1_extract_object.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/dog.jpg # python3 Step2_save_into_seperate.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/dog.jpg 

# lines = []
# with open("imagelist.txt") as f:
#     lines = f.readlines()
# 
# for n in lines[0:100]:
#     n = n.strip()
#     os.system("python3 Step0_object_detection.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../images/test2017/" + n +  ".png")
#     os.system("python3 Step1_extract_object.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../images/test2017/" + n +  ".png")
#     os.system("python3 Step2_save_into_seperate.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../images/test2017/" + n + ".png")
# 
n = sys.argv[1].strip()
os.system("python3 Step0_object_detection.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../../../coco_test_2017/test2017/" + n)
os.system("python3 Step1_extract_object.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../../../coco_test_2017/test2017/" + n)
os.system("python3 Step2_save_into_seperate.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../../../coco_test_2017/test2017/" + n)
