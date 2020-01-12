import time
import io

from google.cloud import storage
from google.cloud import datastore

from flask import Flask
from flask import request
from flask import render_template

import imagehash
from PIL import Image


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['file']
        if f:

            digital_digest = imagehash.average_hash(
                Image.open(f.read())
                )
            f.seek(0)

            # check if exists in datastore

            # if exists, inform frontend
            # else

            uploader = request.args.get('post', 0, type=str)

            datastore_client = datastore.Client()

            key = datastore_client.key(
                'image',
                int(str(time.time()).replace('.', ''))
            )
            ent = datastore.Entity(key=key)

            ent.update({
                'DIGITAL_DIGEST': str(digital_digest),
                'IMG_NAME': f.filename,
                'UPLOADER_EM': uploader,
                'ORG_URL': 'N/A',
                'RCL_URL': 'N/A',
                'VISION_API_TEXT': 'N/A'
            })
            datastore_client.put(ent)

            storage_client = storage.Client()
            bucket = storage_client.bucket('project-ii-gae-bucket-1')

            blob = bucket.blob(f.filename)
            blob.upload_from_string(f.read())

    return render_template('index.html')


# @app.route('/success', methods=['POST'])
# def success():
#     if request.method == 'POST':

#         f = request.files['file']
#         if f:
#             storage_client = storage.Client()
#             bucket = storage_client.bucket('project-ii-gae-bucket-1')

#             blob = bucket.blob(f.filename)
#             blob.upload_from_string(f.read())

#         return render_template('success.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)


# sources - flask & google
#   relative paths in app engine
#   https://stackoverflow.com/questions/61894/whats-a-good-way-to-find-relative-paths-in-google-app-engine
#
#   read Flask uploads from memory
#   https://stackoverflow.com/questions/20015550/read-file-data-without-saving-it-in-flask
#
#   templates in App Engine Flask
#   https://books.google.pl/books?id=9QdYgH5mEi8C&pg=PA120&lpg=PA120&dq=app+engine+templates+folder&source=bl&ots=bbroQ5Sgoo&sig=ACfU3U1VFKmcUTDkCOP9KgUImkfRhuRyGQ&hl=en&sa=X&ved=2ahUKEwjDrLbT5vvmAhWpl4sKHRiZC0QQ6AEwAnoECAoQAQ#v=onepage&q=app%20engine%20templates%20folder&f=false
#
#   uploading files
#   https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
#
# sources - google auth & users
#   google sign-in
#   https://developers.google.com/identity/sign-in/web
#
# sources - images & hash
#   hashing
#   https://ourcodeworld.com/articles/read/1006/how-to-determine-whether-2-images-are-equal-or-not-with-the-perceptual-hash-in-python
#
#   reading Flask FileStorage into Pillow
#   https://stackoverflow.com/questions/17733133/loading-image-from-flasks-request-files-attribute-into-pil-image
#
# sources - datastore
#   datastore python ref
#   https://googleapis.dev/python/datastore/latest/index.html
