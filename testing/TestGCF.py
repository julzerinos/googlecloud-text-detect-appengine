import unittest
import io
from random import randint
import os

from time import sleep

from google.cloud import storage
from google.cloud import pubsub_v1

from PIL import Image

import yaml


def tearDownModule():
    sleep(5)

    with open('static/env.yaml') as y:
        env_var = yaml.load(y, Loader=yaml.FullLoader)

    bucket1 = TestGCF1.storage_client.bucket(env_var['BUCKET1'])
    bucket2 = TestGCF1.storage_client.bucket(env_var['BUCKET2'])

    blob1 = bucket1.blob('test_gcf.png')
    blob2 = bucket2.blob('test_gcf.png')
    blob1.delete()
    blob2.delete()


class TestGCF1(unittest.TestCase):
    @classmethod
    def setUpClass(TestGCF1):
        with open('static/env.yaml') as y:
            env_var = yaml.load(y, Loader=yaml.FullLoader)

        TestGCF1.storage_client = storage.Client()
        TestGCF1.bucket1 = TestGCF1.storage_client.bucket(env_var['BUCKET1'])
        TestGCF1.bucket2 = TestGCF1.storage_client.bucket(env_var['BUCKET2'])

        img = Image.new('RGB', (1028, 1028), color='red')
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()

        new_blob = TestGCF1.bucket1.blob('test_gcf.png')
        new_blob.upload_from_string(
                byte_arr, content_type='image/png'
            )

        sleep(2.5)

    def test014_image_exists_in_bucket_2(self):
        test_blob = self.bucket2.blob('test_gcf.png')
        # Do not use blob.exists()
        # Returns False despite file existing in bucket
        self.assertIsNotNone(test_blob.download_as_string())

    def test015_rescale_success(self):
        test_blob = self.bucket2.blob('test_gcf.png')
        im = Image.open(io.BytesIO(test_blob.download_as_string()), mode='r')
        self.assertEqual(im.size, (512, 512))


class TestGCF2(unittest.TestCase):
    @classmethod
    def setUpClass(TestGCF2):
        with open('static/env.yaml') as y:
            env_var = yaml.load(y, Loader=yaml.FullLoader)

        TestGCF2.subscriber = pubsub_v1.SubscriberClient()
        TestGCF2.sub_path = {
            'sub': TestGCF2.subscriber.subscription_path(
                env_var['PROJECT_ID'], 'rescaled-images-test'),
            'top': TestGCF2.subscriber.topic_path(
                env_var['PROJECT_ID'], 'rescaled-images')
        }

    def test110_published_trigger(self):
        response = self.subscriber.pull(self.sub_path['sub'], 100, return_immediately=True)
        while len(response.received_messages) < 1:
            response = self.subscriber.pull(self.sub_path['sub'], 100, return_immediately=True)
        self.subscriber.acknowledge(self.sub_path['sub'], [msg.ack_id for msg in response.received_messages])

        self.assertIn(
            'test_gcf.png',
            [msg.message.attributes['filename'] for msg in response.received_messages]
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
