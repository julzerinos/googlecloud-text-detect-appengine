# Project II - GAE for GCP course

## Processing images using Cloud Functions

## Sources

#### Cloud Build

#### cloudbuild.yaml

[General](https://cloud.google.com/cloud-build/docs/configuring-builds/create-basic-configuration)
[App Engine](https://cloud.google.com/source-repositories/docs/quickstart-triggering-builds-with-source-repositories)
[Functions](https://medium.com/google-cloud/triggering-cloud-functions-deployments-97691f9b5416)
[Git Deploy](https://cloud.google.com/functions/docs/deploying/repo)
[gcloud](https://cloud.google.com/sdk/gcloud/reference/functions/deploy#--source)

### App engine

#### app.yaml

[Setup for python37](https://cloud.google.com/appengine/docs/standard/python3/config/appref)
[HTTPS always for appspot apps](https://stackoverflow.com/questions/5367974/https-only-in-google-app-engine)

#### flask & google

[relative paths in app engine](https://stackoverflow.com/questions/61894/whats-a-good-way-to-find-relative-paths-in-google-app-engine)
[read Flask uploads from memory](https://stackoverflow.com/questions/20015550/read-file-data-without-saving-it-in-flask)
[templates in App Engine Flask](https://books.google.pl/books?id=9QdYgH5mEi8C&pg=PA120&lpg=PA120&dq=app+engine+templates+folder&source=bl&ots=bbroQ5Sgoo&sig=ACfU3U1VFKmcUTDkCOP9KgUImkfRhuRyGQ&hl=en&sa=X&ved=2ahUKEwjDrLbT5vvmAhWpl4sKHRiZC0QQ6AEwAnoECAoQAQ#v=onepage&q=app%20engine%20templates%20folder&f=false)
[uploading files](https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/)

#### google auth & users

[google sign-in](https://developers.google.com/identity/sign-in/web)
[js functionality](https://developers.google.com/identity/sign-in/web/people)
[html form interception for authentication](https://stackoverflow.com/questions/5384712/capture-a-form-submit-in-javascript)

#### images & hash

[hashing](https://ourcodeworld.com/articles/read/1006/how-to-determine-whether-2-images-are-equal-or-not-with-the-perceptual-hash-in-python)
[reading Flask FileStorage into Pillow](https://stackoverflow.com/questions/17733133/loading-image-from-flasks-request-files-attribute-into-pil-image)

#### datastore

[datastore python ref](https://googleapis.dev/python/datastore/latest/index.html)
