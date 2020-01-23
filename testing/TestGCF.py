import unittest
import io
from random import randint
import os

from google.cloud import storage
from google.cloud import pubsub_v1

from PIL import Image

import yaml


def setUpModule():
    os.environ["TEST_ID"] = str(randint(0, 9999)).zfill(4)


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

        new_blob = TestGCF1.bucket1.blob('test_gcf1.png')
        new_blob.upload_from_string(
                byte_arr, content_type='image/png'
            )

    def test014_image_exists_in_bucket_2(self):
        test_blob = self.bucket2.blob('test_gcf1.png')
        # Do not use blob.exists()
        # Returns False despite file existing in bucket
        self.assertIsNotNone(test_blob.download_as_string())

    def test015_rescale_success(self):
        test_blob = self.bucket2.blob('test_gcf1.png')
        im = Image.open(io.BytesIO(test_blob.download_as_string()), mode='r')
        self.assertEqual(im.size, (512, 512))

    @classmethod
    def tearDownClass(TestGCF1):
        new_blob = TestGCF1.bucket1.blob('test_gcf1.png')
        test_blob = TestGCF1.bucket2.blob('test_gcf1.png')
        if new_blob.exists():
            new_blob.delete()
        if test_blob.exists():
            test_blob.delete()


class TestGCF2(unittest.TestCase):
    @classmethod
    def setUpClass(TestGCF2):
        with open('static/env.yaml') as y:
            env_var = yaml.load(y, Loader=yaml.FullLoader)

        TestGCF2.storage_client = storage.Client()
        TestGCF2.bucket2 = TestGCF2.storage_client.bucket(env_var['BUCKET2'])

        TestGCF2.subscriber = pubsub_v1.SubscriberClient()
        TestGCF2.sub_path = {
            'sub': TestGCF2.subscriber.subscription_path(
                env_var['PROJECT_ID'], 'rescaled-images-test'),
            'top': TestGCF2.subscriber.topic_path(
                env_var['PROJECT_ID'], 'rescaled-images')
        }
        TestGCF2.subscriber.create_subscription(
            TestGCF2.sub_path['sub'],
            TestGCF2.sub_path['top']
            )

        img = Image.new('RGB', (512, 512), color='red')
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()

        new_blob = TestGCF2.bucket2.blob(f'testing_image_{os.environ["TEST_ID"]}.png')
        new_blob.upload_from_string(
                byte_arr, content_type='image/png'
            )

    def test110_published_trigger(self):
        response = self.subscriber.pull(self.sub_path['sub'], max_messages=1)
        self.assertEqual(
            response.received_messages[0].message.data,
            b'An image as been rescaled and placed in bucket-2'
        )
        self.assertEqual(
            response.received_messages[0].message.attributes['filename'],
            f'testing_image_{os.environ["TEST_ID"]}.png'
        )

    @classmethod
    def tearDownClass(TestGCF2):
        TestGCF2.subscriber.delete_subscription(TestGCF2.sub_path['sub'])

        new_blob = TestGCF2.bucket2.blob(f'testing_image_{os.environ["TEST_ID"]}.png')
        new_blob.delete()


if __name__ == '__main__':
    unittest.main(verbosity=2)
