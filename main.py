# sources
#   relative paths in app engine
#   https://stackoverflow.com/questions/61894/whats-a-good-way-to-find-relative-paths-in-google-app-engine
#
#   read Flask uploads from memory
#   https://stackoverflow.com/questions/20015550/read-file-data-without-saving-it-in-flask
#
#   templates in App Engine Flask
#   https://books.google.pl/books?id=9QdYgH5mEi8C&pg=PA120&lpg=PA120&dq=app+engine+templates+folder&source=bl&ots=bbroQ5Sgoo&sig=ACfU3U1VFKmcUTDkCOP9KgUImkfRhuRyGQ&hl=en&sa=X&ved=2ahUKEwjDrLbT5vvmAhWpl4sKHRiZC0QQ6AEwAnoECAoQAQ#v=onepage&q=app%20engine%20templates%20folder&f=false
#


import os

from google.cloud import storage

from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':

        f = request.files['file']
        if f:
            storage_client = storage.Client()
            bucket = storage_client.bucket('project-ii-gae-bucket-1')

            blob = bucket.blob(f.filename)
            blob.upload_from_string(f.read())

        return render_template('success.html')


def __find_file(filefolder, filename):
    return os.path.join(
        os.path.dirname(__file__),
        filefolder,
        filename
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
