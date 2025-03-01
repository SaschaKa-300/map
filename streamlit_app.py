import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
import streamlit.components.v1 as components
import requests
import html

def geocode_address_google(address, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None

st.title("Custom Maps with Your Data")

google_maps_api_key = st.secrets["gmaps_key"]

# Default data
default_data = pd.DataFrame({
    "description": ["Lino's BBQ", "Lei's Küche", "Pamfilya"],
    "address": ["Malplaquetstraße 43, 13347 Berlin", "Seestraße 41, 13353 Berlin", "Luxemburger Str. 1, 13353 Berlin"],
    "type": ["Registrierung", "Erstbestellung", "Bestandskunde"]
})

default_data['latitude'], default_data['longitude'] = zip(*default_data['address'].apply(lambda x: geocode_address_google(x, google_maps_api_key)))

data = default_data.copy()

# Define color mapping based on 'type' column
color_map = {
    "Registrierung": "red",
    "Erstbestellung": "green",
    "Bestandskunde": "blue"
}

if not data.empty:
    # Create map centered at the first valid location
    m = folium.Map(location=[data.iloc[0]['latitude'], data.iloc[0]['longitude']], zoom_start=10)
    
    # Add markers to Folium map with larger icons
    for _, row in data.iterrows():
        marker_color = color_map.get(row.get('type', 'Default'), "gray")
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row.get('description', 'No Description'),
            tooltip="Click for details",
            icon=folium.Icon(color=marker_color, icon_size=(30, 30))  # Increase the size of the pins
        ).add_to(m)
    
    # Display the Folium map
    folium_static(m)
    
    # Embed a Google Map
    st.subheader("Google Maps View")
    map_center = f"{data.iloc[0]['latitude']}, {data.iloc[0]['longitude']}"
    
    # Generate markers with colors for Google Maps with larger pins
    google_markers = "".join([
        f"""
        var marker = new google.maps.Marker({{
            position: new google.maps.LatLng({row['latitude']}, {row['longitude']}),
            map: map,
            icon: {{
                url: 'http://maps.google.com/mapfiles/ms/icons/{color_map.get(row.get('type', 'Default'), 'gray')}-dot.png',
                scaledSize: new google.maps.Size(40, 40)  # Scale marker size (larger)
            }}
        }});

        var infowindow = new google.maps.InfoWindow({{
            content: '<strong>{html.escape(row["description"])}</strong>'
        }});

        marker.addListener('click', function() {{
            infowindow.open(map, marker);
        }});
        """
        for _, row in data.iterrows()
    ])
    
    google_map_html = f"""
    <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}"></script>
    <div id="map" style="height: 500px; width: 100%;"></div>
    <script>
        function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 10,
                center: new google.maps.LatLng({map_center})
            }});
            {google_markers}
        }}
        window.onload = initMap;
    </script>
    """
    
    components.html(google_map_html, height=550)

    # Add a legend below the Google Map
    st.subheader("Legend for Pin Colors")
    st.markdown("""
    - **Red**: Registrierung
    - **Green**: Erstbestellung
    - **Blue**: Bestandskunde
    """)

# Optional CSV upload step at the bottom
st.subheader("Optional: Upload Your Own Data")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

def load_data(file):
    df = pd.read_csv(file)
    return df

if uploaded_file is not None:
    uploaded_data = load_data(uploaded_file)
    st.write("Preview of uploaded data:")
    st.dataframe(uploaded_data.head())
