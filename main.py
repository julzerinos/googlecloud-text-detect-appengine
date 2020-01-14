# App engine backend based on Flask
#
# View related sources and documentation at bottom of the file.
#
# = index =====================================================================
#   - accepts GET and POST HTTP methods
#   - if the POST method is received
#       - check if image has been sent
#           - calculates hash for image
#           - check if image exists in datastore based on hash
#               - if so, prepare optional message to inform user
#               - else the messages informs of upload
#           - unique image id based on current timestamp is created
#           - image is uploaded to bucket-1
#           - image entity is created in datastore
#   - render index.html template with optional message

import time

from google.cloud import storage
from google.cloud import datastore

from flask import Flask
from flask import request, render_template

import imagehash
from PIL import Image


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        f = request.files['file']
        if f:
            # Calculate the digital digest (hash) for the image
            digital_digest = str(imagehash.average_hash(
                Image.open(f.stream)
                ))
            f.seek(0)  # Reset the f.stream to make it readable again

            # Check datastore entities if digital digest exists
            datastore_client = datastore.Client()
            qu = datastore_client.query(kind='image')
            qu.add_filter('DIGITAL_DIGEST', '=', digital_digest)
            if len(list(qu.fetch())):
                message = """Warning: Photo already exists in database.
Email will be sent anyway."""
            else:
                message = "Upload successful. Email will be sent shortly."

            # Parse filename based on timestamp
            im_id = int(str(time.time()).replace('.', ''))
            filename = f"{str(im_id)}.{f.filename.split('.')[-1]}"

            # Prepare bucket-1 connection for image upload
            storage_client = storage.Client()
            bucket = storage_client.bucket('project-ii-gae-bucket-1')
            blob = bucket.blob(filename)
            blob.upload_from_string(
                f.read(),
                content_type=f.content_type
                )

            # Create datastore entity and initialize values
            key = datastore_client.key('image', im_id)
            ent = datastore.Entity(
                key=key,
                exclude_from_indexes=['VISION_API_TEXT']  # for "TextProperty"
                )
            ent.update({
                'DIGITAL_DIGEST': digital_digest,
                'APP_FILENAME': filename,
                'ORG_FILENAME': f.filename,
                'UPLOADER_EM': request.form['email'],
                'ORG_URL': 'N/A',
                'RCL_URL': 'N/A',
                'VISION_API_TEXT': '0' * 1501  # to initialize "TextProperty"
            })
            datastore_client.put(ent)

    return render_template('index.html', message=message)


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
#   js functionality
#   https://developers.google.com/identity/sign-in/web/people
#
#   html form interception for authentication
#   https://stackoverflow.com/questions/5384712/capture-a-form-submit-in-javascript
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
#
# sources - kms
#   kms python reference
#   https://googleapis.dev/python/cloudkms/latest/gapic/v1/api.html
