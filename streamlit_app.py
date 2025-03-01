import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
from geopy.geocoders import Nominatim

def geocode_address(address):
    geolocator = Nominatim(user_agent="geo_app", timeout=10)
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        st.warning(f"Geocoding failed for {address}: {e}")
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
            
            # Define color mapping based on 'type' column
            color_map = {
                "Registrierung": "red",
                "Erstbestellung": "green",
                "Bestandskunde": "blue"
            }
            
            # Add markers
            for _, row in data.iterrows():
                marker_color = color_map.get(row.get('type', 'Default'), "gray")
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=row.get('description', 'No Description'),
                    tooltip="Click for details",
                    icon=folium.Icon(color=marker_color)
                ).add_to(m)
            
            # Display the map
            folium_static(m)

            # Embed a Google Map
            st.subheader("Google Maps View")
            google_maps_api_key = st.secrets["gmaps_key"]
            map_center = f"{data.iloc[0]['latitude']}, {data.iloc[0]['longitude']}"
            markers_js = "".join([f"new google.maps.Marker({{position: new google.maps.LatLng({row['latitude']}, {row['longitude']}), map: map}});" for _, row in data.iterrows()])
            
            google_map_html = f"""
            <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}"></script>
            <div id="map" style="height: 500px; width: 100%;"></div>
            <script>
                function initMap() {{
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 10,
                        center: new google.maps.LatLng({map_center})
                    }});
                    {markers_js}
                }}
                window.onload = initMap;
            </script>
            """
            
            components.html(google_map_html, height=550)


        else:
            st.error("No valid locations found after geocoding.")
    else:
        st.error("CSV must contain an 'address' column.")

