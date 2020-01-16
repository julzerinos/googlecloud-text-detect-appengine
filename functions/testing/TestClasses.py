import unittest

from google.cloud import storage
from google.cloud import pubsub_v1
from google.cloud import vision
from google.cloud import datastore

from ..main import gcf1_rescale, gcf2_inform, gcf3_vision


class TestGCF1(unittest.TestCase):
    def test_image_exists_in_bucket_2(self):
        storage_client = storage.Client()
        source_bucket = storage_client.bucket(os.environ['BUCKET1'])
        target_bucket = storage_client.bucket(os.environ['BUCKET2'])

        new_blob = target_bucket.blob(name)
        new_blob.upload_from_string(
                byte_arr, content_type=event['contentType']
            )


class TestGCF2(unittest.TestCase):
    pass


class TestGCF3(unittest.TestCase):
    pass


if __name__ = '__main__':
    unittest.main()