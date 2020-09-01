import sys 
import os

class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

os.system("export PYTHONPATH=$PYTHONPATH:/root/tensorflow/models/research/:/root/tensorflow/models/research/slim")

with cd("/root/tensorflow/models/research/object_detection/"):
    os.system("python3 tensorflow_sdk_demo.py")

