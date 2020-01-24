import os
import io
from time import sleep

import unittest

from urllib.parse import urlparse as up

from google.cloud import storage
from google.cloud import datastore

import requests as r

from flask import session

from PIL import Image, ImageDraw, ImageFont
import yaml

from main import app


class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(TestIntegration):
        app.testing = True
        app.debug = True
        app.config['SECRET_KEY'] = 'testing_secret'
        TestIntegration.app_client = app.test_client()

        with TestIntegration.app_client.session_transaction() as sess:
            sess['logged_in'] = 'positive-test-gid'

        os.environ['ENV_VAR_FILE_PATH'] = 'static/env.yaml'
        with open('static/env.yaml') as y:
            env_var = yaml.load(y, Loader=yaml.FullLoader)

        TestIntegration.datastore_client = datastore.Client()

        TestIntegration.storage_client = storage.Client()
        TestIntegration.bucket1 = TestIntegration.storage_client.bucket(env_var['BUCKET1'])
        TestIntegration.bucket2 = TestIntegration.storage_client.bucket(env_var['BUCKET2'])

        img = Image.new('RGB', (512, 512), color='red')

        d = ImageDraw.Draw(img)
        d.text((100, 100), "Hello World", fill=(255, 255, 0))

        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()

        TestIntegration.app_client.post(
            '/',
            data={
                'file': (io.BytesIO(byte_arr), 'test_integration.png'),
                'email': 'project.ii.gae.senderbot@gmail.com',
                'gid': 'positive-test-gid'
            },
            follow_redirects=False,
            content_type='multipart/form-data'
        )

        sleep(10)

    def test010_datastore_entries_exist(self):
        qu = self.datastore_client.query(kind='image')
        qu.add_filter('ORG_FILENAME', '=', 'test_integration.png')
        ent = max(list(qu.fetch()), key=lambda x: x.id)

        self.assertTrue(
            ent['APP_FILENAME']
            and
            ent['DIGITAL_DIGEST']
            and
            ent['ORG_FILENAME']
            and
            ent['ORG_URL']
            and
            ent['RSCL_URL']
            and
            ent['UPLOADER_EM']
            and
            ent['VISION_API_TEXT']
        )

    def test015_vision_text(self):
        datastore_client = datastore.Client()
        qu = datastore_client.query(kind='image')
        qu.add_filter('ORG_FILENAME', '=', 'test_integration.png')
        ent = max(list(qu.fetch()), key=lambda x: x.id)

        self.assertIn(
            'Hello World',
            ent['VISION_API_TEXT']
        )

    def test021_images_public(self):
        qu = self.datastore_client.query(kind='image')
        qu.add_filter('ORG_FILENAME', '=', 'test_integration.png')
        ent = max(list(qu.fetch()), key=lambda x: x.id)

        resp1 = r.get(ent['ORG_URL'])
        resp2 = r.get(ent['RSCL_URL'])

        self.assertEqual(
            resp1.status_code, 200
        )
        self.assertEqual(
            resp2.status_code, 200
        )

    @classmethod
    def tearDownClass(TestIntegration):
        sleep(5)

        qu = TestIntegration.datastore_client.query(kind='image')
        qu.add_filter('ORG_FILENAME', '=', 'test_integration.png')
        ent = max(list(qu.fetch()), key=lambda x: x.id)

        test_blob1 = TestIntegration.bucket1.blob(ent['APP_FILENAME'])
        test_blob2 = TestIntegration.bucket2.blob(ent['APP_FILENAME'])

        TestIntegration.datastore_client.delete(ent.key)
        test_blob1.delete()
        test_blob2.delete()


if __name__ == '__main__':
    unittest.main(verbosity=2)
