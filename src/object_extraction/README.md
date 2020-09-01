# **Y**ou **O**nly **L**ook **A**t **C**oefficien**T**s
```
    ██╗   ██╗ ██████╗ ██╗      █████╗  ██████╗████████╗
    ╚██╗ ██╔╝██╔═══██╗██║     ██╔══██╗██╔════╝╚══██╔══╝
     ╚████╔╝ ██║   ██║██║     ███████║██║        ██║   
      ╚██╔╝  ██║   ██║██║     ██╔══██║██║        ██║   
       ██║   ╚██████╔╝███████╗██║  ██║╚██████╗   ██║   
       ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝ 
```

A simple, fully convolutional model for real-time instance segmentation. This is the code for [paper](https://arxiv.org/abs/1904.02689), and for the forseeable future is still in development.

![Example 0](data/yolact_example_0.png)

# Installation
 - Set up a Python3 environment.
 - Install CUDA9.0
 - Install [Pytorch](http://pytorch.org/) 1.0.1 (or higher) and TorchVision.
 - Install some other packages:
   ```Shell
   # Cython needs to be installed before pycocotools
   pip install cython
   pip install opencv-python pillow pycocotools matplotlib 
   pip install Pillow
   ```
   ```

# run it

## step zero:

download the pre-trained model from: 

https://drive.google.com/file/d/1cIyLs8Q-nbsvngTPbXPYHtpxq0_aYhVV/view?usp=sharing

and put it in the current folder.

## object detection
```bashrc
$ python3 Step0_object_detection.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/elephant.png
````
## extract object
```bashrc
$ python3 Step1_extract_object.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/elephant.png
````

## save object into seperate
```bashrc
$ python3 Step2_save_into_seperate.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/elephant.png
````

Then you check your detection results in the `./result/'
