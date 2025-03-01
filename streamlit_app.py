import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
from geopy.geocoders import Nominatim

def geocode_address(address):
    geolocator = Nominatim(user_agent="geo_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

st.title("Custom Google Maps with Your Data")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

def load_data(file):
    df = pd.read_csv(file)
    return df

if uploaded_file is not None:
    data = load_data(uploaded_file)
    st.write("Preview of uploaded data:")
    st.dataframe(data.head())
    
    # Ensure required column exists
    if 'address' in data.columns:
        
        # Convert addresses to coordinates
        data['latitude'], data['longitude'] = zip(*data['address'].apply(geocode_address))
        
        # Filter out rows where geocoding failed
        data = data.dropna(subset=['latitude', 'longitude'])
        
        if not data.empty:
            # Create map centered at the first valid location
            m = folium.Map(location=[data.iloc[0]['latitude'], data.iloc[0]['longitude']], zoom_start=10)
            
            # Add markers
            for _, row in data.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=row.get('description', 'No Description'),
                    tooltip="Click for details"
                ).add_to(m)
            
            # Display the map
            folium_static(m)
        else:
            st.error("No valid locations found after geocoding.")
    else:
        st.error("CSV must contain an 'address' column.")
