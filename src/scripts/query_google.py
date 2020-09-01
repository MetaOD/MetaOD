import requests
# If you are using a Jupyter notebook, uncomment the following line.
from google.cloud import vision
#%matplotlib inline
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw,ImageColor,ExifTags
from io import BytesIO
import sys

# Set image_path to the local path of an image that you want to analyze.
# image_path = "/Users/XXX/work/project/testing-object-detector/data/kite.png"
path = sys.argv[1]

image = Image.open(open(path, "rb"))
imgWidth, imgHeight = image.size
draw = ImageDraw.Draw(image)

client = vision.ImageAnnotatorClient()

with open(path, 'rb') as image_file:
    content = image_file.read()
ig = vision.types.Image(content=content)

w = imgWidth
h = imgHeight

objects = client.object_localization(
    image=ig).localized_object_annotations

# print('Number of objects found: {}'.format(len(objects)))
res = []
for object_ in objects:
    # print('\n{} (confidence: {})'.format(object_.name, object_.score))
    # print('Normalized bounding polygon vertices: ')
    c = 0
    for vertex in object_.bounding_poly.normalized_vertices:
        c += 1
        if c == 1:
            x0 = int(vertex.x * w)
            y0 = int(vertex.y * h)
        elif c == 3:
            x1 = int(vertex.x * w)
            y1 = int(vertex.y * h)
    box = ((x0, y0), (x1, y1))

    points = (
        (x0,y0),
        (x1, y0),
        (x1, y1),
        (x0 , y1),
        (x0, y0)
    )
    # print (label['object'], points)
    #if label['object'] == "Person":
    draw.line(points, fill='#00d400', width=2)

    # Alternatively can draw rectangle. However you can't set line width.
    #draw.rectangle([left,top, left + width, top + height], outline='#00d400')

image.show()
