# sources
#   google storage blob python ref
#   https://googleapis.dev/python/storage/latest/blobs.html
#
#   image manipulations with PIL and google storage
#   https://stackoverflow.com/questions/55941068/change-image-size-with-pil-in-a-google-cloud-storage-bucket-from-a-vm-in-gcloud

import io

from google.cloud import storage

from PIL import Image


def gcf1_rescale(event, context):

    storage_client = storage.Client()
    source_bucket = storage_client.bucket('project-ii-gae-bucket-1')

    blob = source_bucket.blob(event['name']).download_as_string()
    im = Image.open(io.BytesIO(blob))
    x, y = im.size

    # im.thumbnail(512, Image.ANTIALIAS)

    # target_bucket = storage_client.bucket('project-ii-gae-bucket-2')
    # new_blob = target_bucket.blob(event['name'])
    # new_blob.upload_from_string(im.tobytes())

    print(x, y)
    # print("Successfully resized and saved to bucket-2")
