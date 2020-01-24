import os
import io
import unittest

from time import sleep

from google.cloud import storage

from PIL import Image
import yaml

from main import app


class TestFlask(unittest.TestCase):
    @classmethod
    def setUpClass(TestFlask):
        app.testing = True
        app.debug = True
        app.config['SECRET_KEY'] = 'testing_secret'
        TestFlask.app_client = app.test_client()

        with TestFlask.app_client.session_transaction() as sess:
            sess['logged_in'] = 'positive-test-gid'

        os.environ['ENV_VAR_FILE_PATH'] = 'static/env.yaml'
        with open('static/env.yaml') as y:
            env_var = yaml.load(y, Loader=yaml.FullLoader)

        TestFlask.storage_client = storage.Client()
        TestFlask.bucket1 = TestFlask.storage_client.bucket(env_var['BUCKET1'])
        TestFlask.bucket2 = TestFlask.storage_client.bucket(env_var['BUCKET2'])

    def test010_positive_form_post(self):
        img = Image.new('RGB', (1028, 1028), color='red')
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()

        response = self.app_client.post(
            '/',
            data={
                'file': (io.BytesIO(byte_arr), 'test_flask_deployment.png'),
                'email': 'project.ii.gae.senderbot@gmail.com',
                'gid': 'positive-test-gid'
            },
            follow_redirects=True,
            content_type='multipart/form-data'
        )

        self.assertIn(b'<title>Project ii gae</title>', response.data)

    def test011_negative_form_post(self):
        response = self.app_client.post(
            '/',
            data={
                'file': (io.BytesIO(b'0' * 500), 'test_flask_deployment.png'),
                'email': 'project.ii.gae.senderbot@gmail.com',
                'gid': 'positive-test-gid'
            },
            follow_redirects=True,
            content_type='multipart/form-data'
        )

        self.assertIn(b'<title>Error</title>', response.data)
        self.assertIn(b'err_not_image', response.data)

    def test012_oversize_form_post(self):
        response = self.app_client.post(
            '/',
            data={
                'file': (io.BytesIO(b'0' * (1000000 + 1)), 'test_flask_deployment.png'),
                'email': 'project.ii.gae.senderbot@gmail.com',
                'gid': 'positive-test-gid'
            },
            follow_redirects=True,
            content_type='multipart/form-data'
        )

        self.assertIn(b'<title>Error</title>', response.data)
        self.assertIn(b'err_image_size', response.data)

    def test013_undersize_form_post(self):
        response = self.app_client.post(
            '/',
            data={
                'file': (io.BytesIO(b'0' * (100 - 1)), 'test_flask_deployment.png'),
                'email': 'project.ii.gae.senderbot@gmail.com',
                'gid': 'positive-test-gid'
            },
            follow_redirects=True,
            content_type='multipart/form-data'
        )

        self.assertIn(b'<title>Error</title>', response.data)
        self.assertIn(b'err_image_size', response.data)

    def test014_not_logged_in(self):
        response = self.app_client.post(
            '/',
            data={
                'file': (io.BytesIO(b'0' * 5000), 'test_flask_deployment.png'),
                'email': 'project.ii.gae.senderbot@gmail.com',
                'gid': 'fake-test-gid'
            },
            follow_redirects=True,
            content_type='multipart/form-data'
        )

        self.assertIn(b'<title>Error</title>', response.data)
        self.assertIn(b'err_login', response.data)

    def test015_invalid_email(self):
        response = self.app_client.post(
            '/',
            data={
                'file': (io.BytesIO(b'0' * 5000), 'test_flask_deployment.png'),
                'email': 'b4D 3m41L',
                'gid': 'positive-test-gid'
            },
            follow_redirects=True,
            content_type='multipart/form-data'
        )

        self.assertIn(b'<title>Error</title>', response.data)
        self.assertIn(b'err_email_format', response.data)

    def test020_image_stored_bucket1(self):
        test_blob = self.bucket1.blob('test_flask_deployment.png')
        # Do not use blob.exists()
        # Returns False despite file existing in bucket
        self.assertIsNotNone(test_blob.download_as_string())

    @classmethod
    def tearDownClass(TestFlask):
        sleep(5)

        test_blob1 = TestFlask.bucket1.blob('test_flask_deployment.png')
        test_blob2 = TestFlask.bucket2.blob('test_flask_deployment.png')

        test_blob1.delete()
        test_blob2.delete()


if __name__ == '__main__':
    unittest.main(verbosity=2)
