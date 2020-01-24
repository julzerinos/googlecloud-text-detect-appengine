# Processing images using Cloud Functions in the Google App Engine environment

## Introduction

This is an example application deployed on Google App Engine which involves other Google Cloud functionalities in runtime Python 3.7.
Until the project is running, the app may be accessed at https://project-ii-gae.appspot.com/.

An image may be uploaded after logging into a valid google account, after which the user receives an email to the specified email with text detected in the image.

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
Unit tests are implemented for backend components | ✓ | A few tests are supplied as an example to how Cloud Build may run them
Code style | ✓ | Python code written according to Flake8, clutter removed from repository

### Setting Up The Project

Within the repository one may find the `setup.sh` shell script. 
 More specific assumptions may be found within the comments of the files, but in general - the script 
 may be used in an empty project to build the project out of the box in a Google Cloud environment.

The script may be run with `steup.sh [PROJECT_ID] [CLIENT_ID]`, 

where the required fields are empty project ID and a Client ID, which may be created after configuring
 the application consent form.

If one chooses to set up the project manually, the script file may serve as a collection of instructions.

## The Application Overview

The following overview sections are set in order of the project requirments table.

### The Application Accesspoint

Once Google App Engine deploys the application, the following frontend may be accessed by the user.

![Frontend Image](/static/src/srcimg1.png "Frontend Image")

The user must log in to be able to upload an image. After signing in with their Google account through OAuth,
 the upload form becomes available. An image may be uploaded and optionally the recipient email may be changed.
 After upload, the appropriate response is generated (error/success). Sign out is available or the user may repeat
 the process.

The page is serviced through Flask (Python package). A session is created for the logged in user to authorize uploads.
 The form is intercepted upon submit and then posted by AJAX. This is relatively unstable, but should pass for a small
 sized project. 

If an error appears in file uploading, the user will be redirected to an error page with the appropriate error code.

The backend for this upload (Flask) first validates the data for correctness. Then the digital digest is calculated
 (to check if image exists in the database). Afterwards appropriate steps are taken to upload the image to the first 
 bucket with a timestamp-based id. Datastore entity is initialized.

### Further Processing

#### GCF1 - Rescale

The first GCF is triggerd upon an image upload to bucket-1. It downloads the image and rescales it to a width of 512
 pixels while respecting aspect ratio.

The resulting image is uploaded to bucket-2. The related entity in Datastore is updated with both image URLs. 

#### GCF2 - Inform

The second GCF is triggered upon an image upload to bucket-2, ie. after GCF1 runs. The sole existence of this function
 is to publish a message to the pub/sub topic 'rescaled-images'. The message posts an attribute with the filename of the
 uploaded file.

#### GCF3 - Vision

This third and final GCF is the bread and butter of the backend functionality. It is triggered upon a message publication
 to the 'rescaled-images' topic. It stores the related image into memory and uses Google's Vision API to detect visible
 text in the image. This text is stored in the related entity Datastore. 

A simple SMTP server is set-up with a dedicated Google/Gmail account to send the results to the uploader/recipient email.

### Other Functionalities

#### Cloudbuild

A `cloudbuild.yaml` file is present in the repository. If the project is integrated with a Google Cloud Source Repository,
 every `git push` will run `cloudbuild.yaml` if set up in the Cloud Build section. The file runs unit tests on GCF, Flask
 and then integration tests on both components. If these succeed, the newest versions of the GCF and Google App Engine are
 deployed.

#### Unit Tests

Very basic unit tests (Python/unittest) are prepared for the GCFs, Flask and integration of both. Their existence is rather a use for
 presenting how Google Build may run these tests on `git push`.

Below is the list of unit tests.

* GCF
    * GCF1 - test if image was uploaded to second bucket (test014_image_exists_in_bucket_2)
    * GCF1 - test if image was rescaled properly (test015_rescale_success)
    * GCF2 - test if message was properly published (test110_published_trigger)
* Flask
    * test if correct image file is successfully uploaded (test010_positive_form_post)
    * test if negative image file is unsuccessfully uploaded (test011_negative_form_post)
    * test if oversized image is unsuccessfully uploaded (test012_oversize_form_post)
    * test if undersized image is unsuccessfully uploaded (test013_undersize_form_post)
    * test if user not logged in results in unsuccessful upload (test014_not_logged_in)
    * test if invalid email format results in unsuccessful upload (test015_invalid_email)
    * test if the image has been uploaded to bucket-1 (test020_image_stored_bucket1)
* Integration
    * test if the datastore entity has populated fields (test010_datastore_entries_exist)
    * test if text has been detected in image (test015_vision_text)
    * test if the storage blob files are public (test021_images_public)



## Final Thoughts

Google App Engine is yet another solution pulled from the never-ending catalogue of Google products,
 specifically created for producing applications.
The idea is simple: backend, frontend, side-end, whatever-end - the solution will host it and strive
 to run it perfectly.
Unfortunately, that is rarely the case.
The Google platform often riddles the user with false errors or allows itself a casual self-entitled prank 
 by disabling random components of the Google Cloud platform every now and then.
Alas, the terrible contrast between the marketing material and reality is a subject for another time.

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

[pubsub synchron. pull](https://cloud.google.com/pubsub/docs/pull#synchronous_pull)

[encoding as bytes](https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3)

### GCF3

[text detection](https://cloud.google.com/vision/docs/ocr)

[relative paths to container names (pubsup topics)](https://cloud.google.com/pubsub/docs/admin#resource_names)

[sendgrid](https://sendgrid.com/docs/for-developers/sending-email/v3-python-code-example/)
