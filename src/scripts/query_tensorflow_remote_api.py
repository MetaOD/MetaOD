# all right, this is what would happen here:

# 1. scp an image to the remote server
# 2. ssh to the server
# 3. python the a remote module which finish all the tasks (export env; cd; cp; python demo.py)
# 5. scp the json output from the remote server
# 6. parse the json file and return the "res" format used in the env.py module
# 4. logout

import os
import paramiko
import sys

ip='104.198.14.80'
# ip = '35.233.117.165'
port=22
username='root'
password='wsmj2323'

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip,port,username,password)
ftp_client=ssh.open_sftp()

def process_cmd(cmd):
    stdin,stdout,stderr=ssh.exec_command(cmd)
    outlines=stdout.readlines()
    resp=''.join(outlines)

    return resp

def scp_image(path):
    l = "/root/tensorflow/models/research/object_detection/test_image.png"
    ftp_client.put(path, l)


def scp_json():
    l = "/root/tensorflow/models/research/object_detection/output.json"
    ftp_client.get(l, "./output.json")

import json
from PIL import Image, ImageDraw, ExifTags, ImageColor

def parse_draw(path):
    with open('output.json') as f:
        response = json.load(f)

    image = Image.open(open(path,'rb'))
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected face
    for label in response['imgs']['0']['objects']:
        print (label['category'])
        box = label['bbox']
        left = imgWidth * (box['xmin'] / 100.0)
        top = imgHeight * (box['ymin'] / 100.0)
        width = imgWidth * (box['xmax'] / 100.0) - left
        height = imgHeight * (box['ymax'] / 100.0) - top

        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left, top + height),
            (left, top)
        )

        # if label['Name'] == "Person":
        draw.line(points, fill='#00d400', width=2)

    image.show()


def process(image_path):
    scp_image(image_path)
    cmd='python tensorflow_agent.py'
    process_cmd(cmd)
    response = scp_json()

    parse_draw(image_path)

process(sys.argv[1])
