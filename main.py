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

import os
import time

from google.cloud import storage
from google.cloud import datastore

from flask import Flask
from flask import request, render_template

import yaml

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

            # Get bucket name from env variable
            data = None
            with open(os.environ['ENV_VAR_FILE_PATH']) as y:
                data = yaml.load(y, Loader=yaml.FullLoader)

            # Prepare bucket-1 connection for image upload
            storage_client = storage.Client()
            bucket = storage_client.bucket(data['BUCKET1'])
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

    return render_template(
        'index.html',
        message=message,
        sign_in_key=data['SIGNIN_KEY']
        )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
