#!/bin/bash

# OmniBrain Cloud Run Deployment Script
# Note: You should run this in Google Cloud Shell or an environment where 'gcloud' is installed.

# Ensure OPENAI_API_KEY is set in your local environment before deploying
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY is not set."
    echo "Please set it before deploying: export OPENAI_API_KEY='sk-...'"
    exit 1
fi

gcloud run deploy omnibrain \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="OPENAI_API_KEY=${OPENAI_API_KEY}" \
    --min-instances=1 \
    --max-instances=1
