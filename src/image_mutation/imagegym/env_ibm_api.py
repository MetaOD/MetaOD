# this file interact with the remote/local object detector and 
# and collect the detection results by feeding them with one synthesized image 

import requests
import time
from PIL import Image, ImageDraw,ImageColor,ExifTags
from io import BytesIO

def localize_objects(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    image = Image.open(open(path, "rb"))
    x, y = image.size

    files = {'image': open(path, 'rb')}
    params = (
        ('threshold', '0.7'),
    )
    response = requests.post('http://max-object-detector.max.us-south.containers.appdomain.cloud/model/predict', params = params, files=files)

    analysis = response.json()

    res = []
    for label in analysis['predictions']:
        box = label['detection_box']
        top = y * box[0]
        left = x * box[1]
        height = (y * box[2] - y * box[0])
        width = (x * box[3] - x * box[1])
        if (top == 0.0):
            top = 10.0
        if (left == 0.0):
            left = 10.0
        if (height == 0.0):
            height = 10.0
        if (width == 0.0):
            width = 10.0

        box = ((left, left + width), (top, top+height))
        n = label['label'].replace(" ", "_")
        res.append((n, label['probability'] * 100, box))

    return res
