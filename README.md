# Route Planning App

A Streamlit application for visualizing locations on custom maps with Google Maps integration.

## Features

- Display locations on interactive maps (Folium and Google Maps)
- Color-coded markers based on location type
- CSV file upload support
- Geocoding using Google Maps API

## Local Development

1. Install the requirements

   ```
   pip install -r requirements.txt
   ```

2. Set up your Google Maps API key

   Create a `.streamlit/secrets.toml` file:
   ```toml
   gmaps_key = "your-google-maps-api-key"
   ```

3. Run the app

   ```
   streamlit run streamlit_app.py
   ```

## Deployment

This app is configured for deployment to Google Cloud Run via GitHub Actions.

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.
