# Deployment Guide for Google Cloud Run

This project is configured to deploy automatically to Google Cloud Run via GitHub Actions.

## Prerequisites

1. A Google Cloud Project with billing enabled
2. Google Cloud Run API enabled
3. Container Registry API enabled
4. A Google Cloud Service Account with the following roles:
   - Cloud Run Admin
   - Service Account User
   - Storage Admin (for pushing images)

## GitHub Secrets Setup

You need to configure the following secrets in your GitHub repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add the following secrets:

### Required Secrets:

- **`GCP_PROJECT_ID`**: Your Google Cloud Project ID
- **`GCP_SA_KEY`**: Service Account JSON key (download from Google Cloud Console)
- **`GOOGLE_MAPS_API_KEY`**: Your Google Maps API key

### How to get the Service Account Key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to IAM & Admin → Service Accounts
3. Create a new service account or use an existing one
4. Grant the required roles mentioned above
5. Create a JSON key:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose JSON format
   - Download the JSON file
6. Copy the entire contents of the JSON file and paste it as the `GCP_SA_KEY` secret value

## Deployment

### Automatic Deployment

The workflow automatically deploys when you:
- Push to `main` or `master` branch
- Manually trigger the workflow from GitHub Actions tab

### Manual Deployment

You can also deploy manually using the Cloud Build YAML file:

```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions _GOOGLE_MAPS_API_KEY=your-api-key-here
```

Or using gcloud directly:

```bash
gcloud run deploy routeplanning \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_MAPS_API_KEY=your-api-key-here
```

## Workflow Details

The GitHub Actions workflow (`.github/workflows/deploy-cloud-run.yml`) will:
1. Checkout your code
2. Authenticate with Google Cloud
3. Build a Docker image
4. Push the image to Google Container Registry
5. Deploy to Cloud Run with the specified configuration

## Service Configuration

- **Service Name**: `routeplanning`
- **Region**: `us-central1`
- **Port**: `8080`
- **Memory**: `512Mi`
- **CPU**: `1`
- **Max Instances**: `10`
- **Timeout**: `300 seconds`
- **Access**: Public (unauthenticated)

You can modify these settings in the workflow file if needed.

