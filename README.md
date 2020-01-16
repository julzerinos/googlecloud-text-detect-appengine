# Processing images using Cloud Functions in the Google App Engine environment

## Introduction

Google App Engine is yet another solution pulled from the never-ending catalogue of Google products,
 specifically created for producing applications.
The idea is simple: backend, frontend, side-end, whatever-end - the solution will host it and strive
 to run it perfectly.
Unfortunately, that is rarely the case.
The Google platform often riddles the user with false errors or allows itself a casual self-entitled prank 
 by disabling random components of the Google Cloud platform every now and then.
Alas, the terrible contrast between the marketing material and reality is a subject for another time.
Let us get to the matter at hand - an example of a python3.7 runtime app hosted on the Google App Engine.

## The Project Overview

### Intent

The following technologies and skills are used:
* Developing an application running on Google App Engine in Python 3.7 runtime
* Using Google Source Repositories as source control system
* Using Google Cloud Ruild for building container images and deployment automation
* Using Google managed database technologies as data persistency, i.e. Cloud Datastore and Cloud Storage
* Using Google Cloud Functions to act in response to events
* Orchestrating Continuous Integration system to build application artefacts
* Preparing proper deployment instrumentation

### User Flow

The user flow defined for the project is as follows:

1. As a user I can navigate to a website where I can log in using GCP account credentials (users without valid GCP credentials cannot log into the system). 
2. After successful login I can upload an image in JPG or PNG format and this image is stored in Cloud Storage bucket (see Note 2) 
3. I have a Cloud Function GCF#1 with a Cloud Storage trigger that discovers that an image was uploaded to Storage bucket#1. Cloud Function scales down the picture and stores the result in Cloud Storage bucket#2. 
4. There is another Cloud Function (GCF#2) that processes images from bucket#2. GCF#2 discovers transformed images stored in bucket#2 and puts the message in Pub/Sub channel that is a trigger for GCF#3. \
5. GCF#3 makes a call to Vision API and discover text visible in the image. Result of Vision API call is stored in the Datastore. 
6. Finally, GCF#3 should send an email with the link to the image to GCP user and. Email should inform the user about successful or not successful operation of image transformation. Email should contain signed URLs to original and transformed image. Email should also contain text discovered for this specific image by Vision API 
7. I can press 'Logout' button to log out of the service. Once I press 'Logout' I'm navigated back to login/initial page where there is a "Login" button I can use to log back into the system. 

The implementation of the above user flow takes certain liberties, but those are explained below.

### Project Requirements

Requirement | Fulfilled | Notes
--- | --- | ---
Application works according to user flow | ✓ | -
Application is described in a `README.md` | ✓ | This is it
Users can log into the application using GCP accounts (restricted access). HTTPS only is supported. It is possible to log out | ✓ | GCP accounts are assumed to be all Google accounts. Authentication is shallow (file upload authentication is done in frontend). HTTPS is secured by built-in GAE mechanics
App stores image files in a Cloud Storage bucket using unique identifiers. KMS is used to create Customer Managed Encryption on uplaoded files | ✓ | Timestamps are used as identifiers for images
Datastore is used to keep information on *image uploader*, *image name*, *digital digest*, *signed url to original*, *signed url to rescaled* and *Vision API text* | ✓ | Digital digest (hash) is calculated based on bytes string
Source code is stored in Google Source Repositories | ✓ | For sharing purposes, code is stored on GitHub repositories
Google Cloud Function 1 stores and rescales images | ✓ | -
Google Cloud Function 3 is triggered by pub/sub, uses Vision API to find text in image and sends an email to uploader | ✓ | -
Cloud Build builds newer version of application when changes are commited to repo | ✓ | Solved with Cloud Build Triggers (beta)
Cloud Build deploys newer version of application into GAE | ✓ | -
Cloud Build deploys newer version of Cloud Functions on repo git push | ✓ | -
Unit tests are implemented for backend components | ✗ | No tests are included in the project. Application works "as is"
Code style | ✓ | Python code written according to Flake8, clutter removed from repository

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

### GCF1

#### storage & images

[google storage blob python ref](https://googleapis.dev/python/storage/latest/blobs.html)

[google storage buckets python ref](https://googleapis.dev/python/storage/latest/buckets.html)

[image manipulations with PIL and google storage](https://stackoverflow.com/questions/55941068/change-image-size-with-pil-in-a-google-cloud-storage-bucket-from-a-vm-in-gcloud)

[blobs saved as strings of bytes](https://stackoverflow.com/questions/46078088/how-to-upload-a-bytes-image-on-google-cloud-storage-from-a-python-script)

[maintain aspect ratio](https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio)

### GCF2

[pubsub ref](https://googleapis.dev/python/pubsub/latest/index.html)

[encoding as bytes](https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3)

### GCF3

[text detection](https://cloud.google.com/vision/docs/ocr)

[relative paths to container names (pubsup topics)](https://cloud.google.com/pubsub/docs/admin#resource_names)

[sendgrid](https://sendgrid.com/docs/for-developers/sending-email/v3-python-code-example/)
