import requests
# If you are using a Jupyter notebook, uncomment the following line.
#%matplotlib inline
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw,ImageColor,ExifTags
from io import BytesIO
import sys

# Set image_path to the local path of an image that you want to analyze.
image_path = "kite.png"

files = {'image': open('./' + sys.argv[1], 'rb')}
params = (
    ('threshold', '0.7'),
)
response = requests.post('http://max-object-detector.max.us-south.containers.appdomain.cloud/model/predict', params = params, files=files)

analysis = response.json()

image = Image.open(open("./" + sys.argv[1], "rb"))
x, y = image.size
draw = ImageDraw.Draw(image)

for label in analysis['predictions']:
    print (label)
    box = label['detection_box']
    top = y * box[0]
    left = x * box[1]
    height = (y * box[2] - y * box[0])
    width = (x * box[3] - x * box[1])

    points = (
        (left,top),
        (left + width, top),
        (left + width, top + height),
        (left , top + height),
        (left, top)
    )
    print (label['label'], points)
    #if label['object'] == "Person":
    draw.line(points, fill='#00d400', width=2)

    # Alternatively can draw rectangle. However you can't set line width.
    #draw.rectangle([left,top, left + width, top + height], outline='#00d400')

image.show()
