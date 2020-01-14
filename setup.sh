#!/bin/bash

echo "Enter project id: "
read PROJECT_ID

# Set project ID
gcloud config set project $PROJECT_ID
echo "Project set to project ID: " $PROJECT_ID

# Enable APIs
gcloud services enable appengine.googleapis.com
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
echo "Enabled related APIs"

gsutil mb gs://project-ii-gae-bucket-1/
gsutil mb gs://project-ii-gae-bucket-2/
echo "Created Buckets"

gcloud pubsub topics create rescaled-images
echo "Created PUB/SUB topic"

gcloud app create --project=$PROJECT_ID
echo "Initialized App Engine"
gcloud app deploy
echo "App deployed"

gcloud functions deploy gcf1_rescale --source=https://source.developers.google.com/projects/project-ii-gae/repos/project-II-gae/moveable-aliases/master/paths/functions --trigger-bucket=project-ii-gae-bucket-1 --runtime=python37 --env-vars-file=env.yaml
gcloud functions deploy gcf2_inform --source=https://source.developers.google.com/projects/project-ii-gae/repos/project-II-gae/moveable-aliases/master/paths/functions --trigger-bucket=project-ii-gae-bucket-2 --runtime=python37 --env-vars-file=env.yaml
gcloud functions deploy gcf3_vision --source=https://source.developers.google.com/projects/project-ii-gae/repos/project-II-gae/moveable-aliases/master/paths/functions --trigger-topic=rescaled-images --runtime=python37 --env-vars-file=env.yaml
echo "GCF deployed"

gcloud builds submit --config cloudbuild.yaml .
# Triggers not supported in command line
echo "Initialized Cloud Build"