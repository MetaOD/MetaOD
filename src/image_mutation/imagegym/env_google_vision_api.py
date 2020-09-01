# this file interact with the remote/local object detector and 
# and collect the detection results by feeding them with one synthesized image 

# sample code from Google 
# https://cloud.google.com/vision/docs/detecting-objects#object-localization-local-python

from google.cloud import vision
from PIL import Image

def localize_objects(client, path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
   # client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    im = Image.open(path)
    w, h = im.size

    objects = client.object_localization(
        image=image).localized_object_annotations

    #print('Number of objects found: {}'.format(len(objects)))
    res = []
    for object_ in objects:
        #print('\n{} (confidence: {})'.format(object_.name, object_.score))
        #print('Normalized bounding polygon vertices: ')

        #for vertex in object_.bounding_poly.normalized_vertices:
        #    print(' - ({}, {})'.format(vertex.x, vertex.y))

        c = 0
        for vertex in object_.bounding_poly.normalized_vertices:
            c += 1
            if c == 1:
                x0 = int(vertex.x * w)
                y0 = int(vertex.y * h)
            elif c == 3:
                x1 = int(vertex.x * w)
                y1 = int(vertex.y * h)
        if (x0 == 0):
            x0 = 10
        if (x1 == 0):
            x1 = 10
        if (y0 == 0):
            y0 = 10
        if (y1 == 0):
            y1 = 10
        box = ((x0, x1), (y0, y1))
        n = object_.name
        n = n.replace(" ", "_")
        res.append((n, object_.score * 100, box))

    print (res)
    return res

# localize_objects("./wakeupcat.jpg")
# localize_objects("../../../../../coco_test_2017/test2017/000000267860.png")
