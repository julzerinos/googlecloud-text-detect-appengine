# sources - GCF1
#   google storage blob python ref
#   https://googleapis.dev/python/storage/latest/blobs.html
#
#   google storage buckets python ref
#   https://googleapis.dev/python/storage/latest/buckets.html
#
#   image manipulations with PIL and google storage
#   https://stackoverflow.com/questions/55941068/change-image-size-with-pil-in-a-google-cloud-storage-bucket-from-a-vm-in-gcloud
#
#   blobs saved as strings of bytes
#   https://stackoverflow.com/questions/46078088/how-to-upload-a-bytes-image-on-google-cloud-storage-from-a-python-script
#
#   maintain aspect ratio
#   https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
#
# sources - GCF2
#   pubsub ref
#   https://googleapis.dev/python/pubsub/latest/index.html
#
#   encoding as bytes
#   https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3


import os
import io

from google.cloud import storage
from google.cloud import pubsub_v1
from google.cloud import vision

from PIL import Image


def gcf1_rescale(event, context):

    # Prepare rep variables
    name = event['name']

    # Open client for accessing Storage
    storage_client = storage.Client()

    # Prepare buckets used in process
    source_bucket = storage_client.bucket(os.environ['BUCKET1'])
    target_bucket = storage_client.bucket(os.environ['BUCKET2'])

    # Get uploaded file
    blob = source_bucket.blob(name).download_as_string()

    # Open and rescale
    # Rescales width to 512 and maintains aspect ratio
    im = Image.open(io.BytesIO(blob), mode='r')
    img_format = im.format

    basewidth = 512
    x, y = im.size
    wpercent = (basewidth/float(x))
    hsize = int((float(y)*float(wpercent)))
    im = im.resize((basewidth, hsize), Image.ANTIALIAS)

    # Save bytes
    byte_arr = io.BytesIO()
    im.save(byte_arr, format=img_format)
    byte_arr = byte_arr.getvalue()

    # Create new blob and upload
    new_blob = target_bucket.blob(name)
    new_blob.upload_from_string(
            byte_arr, content_type=event['contentType']
        )

    # Debug logging
    print(f"Success: {name} scaled and saved to bucket-2")


def gcf2_inform(event, context):
    publisher = pubsub_v1.PublisherClient()

    publisher.publish(
        'rescaled-images',
        b'An image as been rescaled and placed in bucket-2',
        filename=event['name']
        )


def gcf3_vision(event, context):
    client = vision.ImageAnnotatorClient()
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ['BUCKET2'])

    print(event, context)

    # blob = bucket.blob(event['file']).download_as_string()

    # im = vision.types.Image(
    #     content=
    #     )
