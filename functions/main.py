import sys

from google.cloud import storage


def gcf1_rescale(event, context):

    storage_client = storage.Client()
    source_bucket = storage_client.bucket('project-ii-gae-bucket-1')

    blob = bucket.blob(event['name'])

    file = event
    print(f"BLOB ==== {blob}.")

