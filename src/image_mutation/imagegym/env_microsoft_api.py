import requests
import time
# If you are using a Jupyter notebook, uncomment the following line.
#%matplotlib inline
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw,ImageColor,ExifTags
from io import BytesIO


def localize_objects(path):
    # Replace <Subscription Key> with your valid subscription key.
    # subscription_key = "772867bc99ed49549a9739b8ee14226b"
    subscription_key = "cb59ce55ac614ca5a494f75f51e6074a"
    assert subscription_key

    # time.sleep(1)

    # You must use the same region in your REST call as you used to get your
    # subscription keys. For example, if you got your subscription keys from
    # westus, replace "westcentralus" in the URI below with "westus".
    #
    # Free trial subscription keys are generated in the "westus" region.
    # If you use a free trial subscription key, you shouldn't need to change
    # this region.
    # vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
    vision_base_url = "https://francecentral.api.cognitive.microsoft.com/vision/v2.0/"
    analyze_url = vision_base_url + "analyze"
    # Set image_path to the local path of an image that you want to analyze.
    image_path = path
    # Read the image into a byte array
    image_data = open(image_path, "rb").read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
                  'Content-Type': 'application/octet-stream'}
    params     = {'visualFeatures': 'Objects'}
    response = requests.post(
        analyze_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    # print(analysis)
    # image_caption = analysis["description"]["captions"][0]["text"].capitalize()
    # Display the image and overlay it with the caption.

    image = Image.open(open(image_path, "rb"))
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    res = []
    # calculate and display bounding boxes for each detected face
    for label in analysis['objects']:
        # print (label)
        print (label)
        box = label['rectangle']
        left = box['x']
        top = box['y']
        width = box['w']
        height = box['h']
        if (top == 0.0):
            top = 10.0
        if (left == 0.0):
            left = 10.0
        if (height == 0.0):
            height = 10.0
        if (width == 0.0):
            width = 10.0

        box = ((left, left + width), (top, top+height))
        n = label['object'].replace(" ", "_")
        res.append((n, label['confidence'] * 100, box))

    return res
