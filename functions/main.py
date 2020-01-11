import sys
import io

from google.cloud import storage

from PIL import Image

def gcf1_rescale(event, context):

    storage_client = storage.Client()
    source_bucket = storage_client.bucket('project-ii-gae-bucket-1')

    blob = source_bucket.blob(event['name']).download_as_string()
    im = Image.open(io.BytesIO(blob))
    im.thumbnail(512, Image.ANTIALIAS)

    target_bucket = storage_client.bucket('project-ii-gae-bucket-2')
    new_blob = target_bucket.blob(event['name'])
    new_blob.upload_from_string(im.tobytes())    

    print(f"Successfully resized and saved to bucket-2")

