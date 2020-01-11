import sys

from google.cloud import storage

from google.appengine.api import images


def gcf1_rescale(event, context):

    #   storage_client = storage.Client()
    #   target_bucket = storage_client.bucket('project-ii-gae-bucket-2')


    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    file = event
    print(f"Processing file:\n\n{event}\n\n{context}.")

