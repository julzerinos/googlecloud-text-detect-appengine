# App engine backend based on Flask
#
# General notes
#   As the google app engine app.yaml configuration file only accepts
#   singular env var, there is only one env var which points to a yaml
#   file containg all the required "env var"s. These are stored in
#   static/env.yaml
#
# index() method general flow
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
import re

from google.cloud import storage
from google.cloud import datastore

from flask import Flask
from flask import request, render_template, redirect, url_for, session

import yaml

import imagehash
from PIL import Image


app = Flask(__name__)
app.secret_key = "hahagoogleveryfunny"


@app.route('/', methods=['GET', 'POST'])
def index():
    # Get env var list from env var yaml file
    if 'ENV_VAR_FILE_PATH' not in os.environ:
        os.environ['ENV_VAR_FILE_PATH'] = 'static/env.yaml'
    with open(os.environ['ENV_VAR_FILE_PATH']) as y:
        env_var = yaml.load(y, Loader=yaml.FullLoader)

    if request.method == 'POST':
        f = request.files.get('file')
        if f:
            # Check log in
            if 'gid' not in request.form or \
                    'logged_in' not in session or \
                    request.form['gid'] != session['logged_in']:
                return redirect(url_for('error', message="err_login"))

            # Validate email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", request.form['email']):
                return redirect(url_for('error', message="err_email_format"))

            # Check if 100B =< len(file) =< 2MB
            f.seek(0, os.SEEK_END)
            file_length = f.tell()
            if file_length > 1000000 or file_length < 100:
                return redirect(url_for('error', message="err_image_size"))

            # Verify if file is an image
            try:
                im = Image.open(f.stream)
                im.verify()
            # Using bare except due to lack of information on PIL exception
            except:  # noqa
                return redirect(url_for('error', message="err_not_image"))
            f.seek(0)  # Reset the f.stream to make it readable again

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

            if f.filename == 'test_flask_deployment.png':
                filename = f.filename

            # Prepare bucket-1 connection for image upload
            storage_client = storage.Client()
            bucket = storage_client.bucket(env_var['BUCKET1'])
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
                'ORG_URL': '',
                'RSCL_URL': '',
                'VISION_API_TEXT': '0' * 1501  # to initialize "TextProperty"
            })
            datastore_client.put(ent)

            return redirect(url_for(
                'index',
                message=message
                ))

    return render_template(
        'index.html',
        message=request.args.get('message') or "",
        sign_in_key=env_var['SIGNIN_KEY']
    )


@app.route('/error')
def error():
    return render_template(
        'error.html',
        message=request.args.get('message')
    )


@app.route('/login', methods=['POST'])
def login():
    if request.values.get('type') == 'in':
        session['logged_in'] = request.values.get('loggedIn')
        app.logger.info(request.values.get('loggedIn') + " logged in.")
    if request.values.get('type') == 'out':
        session.pop('logged_in')
        app.logger.info(request.values.get('loggedIn') + " logged out.")
    return "success"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
