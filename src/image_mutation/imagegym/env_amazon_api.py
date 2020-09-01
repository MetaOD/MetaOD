# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor


def localize_objects(path):
    # Change bucket and photo to your S3 Bucket and image.
    # path ='./kite.jpg'
 
    client=boto3.client('rekognition')

    image = Image.open(open(path,'rb'))
    row,col = image.size
    stream = io.BytesIO()
    image.save(stream, format=image.format)
    image_binary = stream.getvalue()

    client = boto3.client('rekognition')
    response = client.detect_labels(Image={'Bytes': image_binary}, MaxLabels=50)

    # draw = ImageDraw.Draw(image)

    # print('Detected labels for ' + photo) 
    # print()   
    res = []
    for label in response['Labels']:
        # print ("Label: " + label['Name'])

        # print ("Confidence: " + str(label['Confidence']))
        # print ("Instances:")
        for instance in label['Instances']:
            # print ("Label: " + label['Name'])
            # print ("  Bounding box")
            # print ("    Top: " + str(instance['BoundingBox']['Top']))
            # print ("    Left: " + str(instance['BoundingBox']['Left']))
            # print ("    Width: " +  str(instance['BoundingBox']['Width']))
            # print ("    Height: " +  str(instance['BoundingBox']['Height']))
            # print ("    : " +  str(instance['BoundingBox']))
            # print ("  Confidence: " + str(instance['Confidence']))
            # print()
            box = (instance['BoundingBox']['Left'], instance['BoundingBox']['Left'] + instance['BoundingBox']['Width'], instance['BoundingBox']['Top'], instance['BoundingBox']['Top'] + instance['BoundingBox']['Height'])
            box = ((int(row*box[0]), int(row*box[1])), (int(col*box[2]), int(col*box[3])))
            x0 = box[0][0]
            x1 = box[0][1]
            y0 = box[1][0]
            y1 = box[1][1]
            if (x0 == 0):
                x0 = 10
            if (x1 == 0):
                x1 = 10
            if (y0 == 0):
                y0 = 10
            if (y1 == 0):
                y1 = 10

            box = ((x0, x1), (y0, y1))
            n = label['Name'].replace(" ", "_")
            res.append((n, instance['Confidence'], box))

        # print ("Parents:")
        # for parent in label['Parents']:
        #     print ("   " + parent['Name'])
        # print ("----------")
        # print ()

    return res
