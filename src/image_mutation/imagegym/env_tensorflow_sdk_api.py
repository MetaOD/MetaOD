import io
import json
from PIL import Image, ImageDraw, ExifTags, ImageColor



def process_cmd(ssh, cmd):
    stdin,stdout,stderr=ssh.exec_command(cmd)
    outlines=stdout.readlines()
    resp=''.join(outlines)

    return resp


def scp_image(ssh, path):
    ftp_client = ssh.open_sftp()
    # l = "/home/XXX/tensorflow/models/research/object_detection/test_image.png"
    l = "/root/tensorflow/models/research/object_detection/test_image.png"
    ftp_client.put(path, l)


def scp_json(ssh):
    ftp_client = ssh.open_sftp()
    # l = "/home/XXX/tensorflow/models/research/object_detection/output.json"
    l = "/root/tensorflow/models/research/object_detection/output.json"
    ftp_client.get(l, "./output.json")


def parse_draw(path):
    with open('output.json') as f:
        response = json.load(f)

    image = Image.open(open(path,'rb'))
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    res = []

    for label in response['imgs']['0']['objects']:
        box = label['bbox']
        x0 = imgWidth * (box['xmin'] / 100.0)
        y0 = imgHeight * (box['ymin'] / 100.0)
        x1 = imgWidth * (box['xmax'] / 100.0)
        y1 = imgHeight * (box['ymax'] / 100.0)

        if (x0 == 0.0):
            x0 = 10.0
        if (x1 == 0.0):
            x1 = 10.0
        if (y0 == 0.0):
            y0 = 10.0
        if (y1 == 0.0):
            y1 = 10.0
        box = ((int(x0), int(x1)), (int(y0), int(y1)))
        n = label['category'].replace(" ", "_")
        res.append((n, label['score'] * 100, box))

    return res

def localize_objects(ssh_client, path):
    # path ='./kite.jpg'
    scp_image(ssh_client, path)
    cmd = 'python3 tensorflow_agent.py'
    process_cmd(ssh_client, cmd)
    response = scp_json(ssh_client)

    res = parse_draw(path)
    return res

