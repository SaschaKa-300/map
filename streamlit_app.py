import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
import streamlit.components.v1 as components
import requests
import html

# Function to get latitude and longitude from Google Geocode API
def geocode_address_google(address, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None

# Function to get optimized route and directions from Google Routes API
def get_route(locations, api_key):
    url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "origin": {"location": {"latLng": {"latitude": locations[0][0], "longitude": locations[0][1]}}},
        "destination": {"location": {"latLng": {"latitude": locations[0][0], "longitude": locations[0][1]}}},
        "intermediates": [{"location": {"latLng": {"latitude": lat, "longitude": lng}}} for lat, lng in locations[1:]],
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE"
    }
    
    response = requests.post(url, headers=headers, json=payload).json()
    if "routes" in response:
        route = response["routes"][0]
        steps = []
        polyline_points = route["polyline"]["encodedPolyline"]
        
        for leg in route["legs"]:
            for step in leg["steps"]:
                instructions = step["navigationInstruction"]["instructions"]
                distance = step["distanceMeters"]
                steps.append(f"{html.unescape(instructions)} ({distance} meters)")
        
        return steps, polyline_points
    return [], ""

st.title("Custom Maps with Optimized Route")

google_maps_api_key = st.secrets["gmaps_key"]

default_data = pd.DataFrame({
    "description": ["Lino's BBQ", "Lei's Küche", "Pamfilya"],
    "address": ["Malplaquetstraße 43, 13347 Berlin", "Seestraße 41, 13353 Berlin", "Luxemburger Str. 1, 13353 Berlin"],
    "type": ["Registrierung", "Erstbestellung", "Bestandskunde"]
})

default_data['latitude'], default_data['longitude'] = zip(*default_data['address'].apply(lambda x: geocode_address_google(x, google_maps_api_key)))

data = default_data.copy()

color_map = {
    "Registrierung": "red",
    "Erstbestellung": "green",
    "Bestandskunde": "blue"
}

if not data.empty:
    locations = [(row['latitude'], row['longitude']) for _, row in data.iterrows()]
    steps, polyline_points = get_route(locations, google_maps_api_key)
    
    m = folium.Map(location=[data.iloc[0]['latitude'], data.iloc[0]['longitude']], zoom_start=12)
    
    for _, row in data.iterrows():
        marker_color = color_map.get(row.get('type', 'gray'))
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['description'],
            tooltip=row['description'],
            icon=folium.Icon(color=marker_color)
        ).add_to(m)
    
    if polyline_points:
        folium.PolyLine(locations, color="blue", weight=5, opacity=0.7).add_to(m)
    
    folium_static(m)
    
    st.subheader("Step-by-Step Navigation Instructions")
    for i, step in enumerate(steps):
        st.markdown(f"**Step {i+1}:** {step}")
    
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
