# sources
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

import io

from google.cloud import storage

from PIL import Image


def gcf1_rescale(event, context):

    # Prepare rep variables
    name = event['name']

    # Open client for accessing Storage
    storage_client = storage.Client()

    # Prepare buckets used in process
    source_bucket = storage_client.bucket('project-ii-gae-bucket-1')
    target_bucket = storage_client.bucket('project-ii-gae-bucket-2')

    # Get uploaded file
    blob = source_bucket.blob(name).download_as_string()

    # Rescale
    im = Image.open(io.BytesIO(blob))

    # im.thumbnail(512, Image.ANTIALIAS)

    # Create new blob and upload
    new_blob = target_bucket.blob(name)
    new_blob.upload_from_string(
            im, content_type=event['contentType']
        )

    # Debug logging
    print(f"Success: {name} scaled and saved to bucket-2")
