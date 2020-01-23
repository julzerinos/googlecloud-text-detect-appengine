#!/bin/bash

# Bash script which automates setup in empty google project
# Assumptions - these are required steps to be taken by the user
#   - The project has been created and project id is known
#   - Appropriate permissions are available to user (at least Project Editor)
#   - Billing is setup for the account/project
#   - The repository has been cloned to the appropriate project folder
#   - The script is run in the cloned git repository/project folder
#   - A consent screen is configured for the project
#   - An OAuth Client key has been generated
#     (see https://console.developers.google.com/apis/credentials
#     or APIs & Services > Credentials)
#       - In the field "authorized javascript origins" enter https://YOUR_PROJECT_ID.appspot.com
#       - Or fill in this field with the appspot uri after app engine deployment
# 
# Notes
#   - Due to the unstable and violent environment that is Google Cloud,
#     please be prepared to debug any errors which the script may evoke
#   - If setup has been done manually, please make sure each step has 
#     been taken into account.
#
# Usage
#   ./setup.sh PROJECT_ID CLIENT_ID
#

PROJECT_ID=$1
CLIENT_ID=$2

gcloud config set project $PROJECT_ID
echo "Project set to project ID: "$PROJECT_ID

echo "Activate related APIs"
gcloud services enable appengine.googleapis.com        
gcloud services enable bigquery.googleapis.com         
gcloud services enable bigquerystorage.googleapis.com  
gcloud services enable cloudapis.googleapis.com 
gcloud services enable cloudbuild.googleapis.com            
gcloud services enable clouddebugger.googleapis.com         
gcloud services enable cloudfunctions.googleapis.com        
gcloud services enable cloudkms.googleapis.com              
gcloud services enable cloudresourcemanager.googleapis.com  
gcloud services enable cloudtrace.googleapis.com            
gcloud services enable compute.googleapis.com               
gcloud services enable containerregistry.googleapis.com     
gcloud services enable datastore.googleapis.com             
gcloud services enable logging.googleapis.com               
gcloud services enable monitoring.googleapis.com            
gcloud services enable oslogin.googleapis.com               
gcloud services enable pubsub.googleapis.com                
gcloud services enable servicemanagement.googleapis.com     
gcloud services enable serviceusage.googleapis.com          
gcloud services enable source.googleapis.com                
gcloud services enable sourcerepo.googleapis.com            
gcloud services enable sql-component.googleapis.com         
gcloud services enable storage-api.googleapis.com           
gcloud services enable storage-component.googleapis.com     
gcloud services enable vision.googleapis.com
echo

echo "Bucket creation"
while true; do
    BUCKET1="bucket-1-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 54 | head -n 1)"
    if gsutil mb -l EUROPE-WEST1 gs://$BUCKET1/; then
        break;
    fi
done
while true; do
    BUCKET2="bucket-2-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 54 | head -n 1)"
    if  gsutil mb -l EUROPE-WEST1 gs://$BUCKET2/; then
        break;
    fi
done

touch static/env.yaml
printf "BUCKET1: '%s'\n" $BUCKET1 >| static/env.yaml
printf "BUCKET2: '%s'\n" $BUCKET2 >> static/env.yaml
printf "GMAIL_APP_KEY: '%s'\n" "rvkzzmvcqzgpvsvr" >> static/env.yaml
printf "SIGNIN_KEY: '%s'\n" $CLIENT_ID >> static/env.yaml
printf "PROJECT_ID: '%s'\n" $PROJECT_ID >> static/env.yaml
echo

echo "KMS & CME Initialization"
gcloud kms keyrings create project-ii-gae-keyring --location europe-west1
gcloud kms keys create bucket-encryption \
  --location europe-west1 \
  --keyring project-ii-gae-keyring \
  --purpose encryption

gsutil kms authorize \
    -k projects/$PROJECT_ID/locations/europe-west1/keyRings/project-ii-gae-keyring/cryptoKeys/bucket-encryption
gsutil kms encryption \
    -k projects/$PROJECT_ID/locations/europe-west1/keyRings/project-ii-gae-keyring/cryptoKeys/bucket-encryption \
    gs://$BUCKET1
echo

echo "PUB/SUB topic creation"
gcloud pubsub topics create rescaled-images
gcloud pubsub subscriptions create rescaled-images-test \
    --topic=projects/project-ii-gae/topics/rescaled-images \
    --topic-project=$PROJECT_ID
echo

echo "App deployment"
gcloud app create --project=$PROJECT_ID --region=europe-west
echo "Initialized App Engine"
yes Y | gcloud app deploy app.yaml
echo

echo "GCF deployment"
gcloud functions deploy gcf1_rescale \
    --source="`pwd`/functions" \
    --trigger-bucket=$BUCKET1 \
    --allow-unauthenticated \
    --runtime=python37 \
    --env-vars-file=static/env.yaml
gcloud functions deploy gcf2_inform \
    --source="`pwd`/functions" \
    --trigger-bucket=$BUCKET2 \
    --allow-unauthenticated \
    --runtime=python37 \
    --env-vars-file=static/env.yaml
gcloud functions deploy gcf3_vision \
    --source="`pwd`/functions" \
    --trigger-topic="rescaled-images" \
    --allow-unauthenticated \
    --runtime=python37 \
    --env-vars-file=static/env.yaml
echo
