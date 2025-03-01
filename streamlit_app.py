import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
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

# Function to get opening hours using Google Places API
def get_opening_hours(lat, lng, api_key):
    place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=50&key={api_key}"
    response = requests.get(place_url).json()
    
    if response['status'] == 'OK':
        place_id = response['results'][0]['place_id']
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={api_key}"
        details_response = requests.get(details_url).json()
        
        if details_response['status'] == 'OK':
            result = details_response['result']
            opening_hours = result.get('opening_hours', {}).get('weekday_text', [])
            return opening_hours
    return None

# Function to get optimized route using Google Directions API
def get_optimized_route(locations, api_key):
    origin = locations[0]
    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:]])
    
    route_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={origin}&waypoints=optimize:true|{waypoints}&key={api_key}"
    response = requests.get(route_url).json()
    
    if response['status'] == 'OK':
        optimized_route = []
        for leg in response['routes'][0]['legs']:
            for step in leg['steps']:
                optimized_route.append(step['end_location'])
        return optimized_route
    return []

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

# Step 1: Get Opening Hours for each location
for index, row in data.iterrows():
    opening_hours = get_opening_hours(row['latitude'], row['longitude'], google_maps_api_key)
    data.at[index, 'opening_hours'] = opening_hours if opening_hours else 'No data available'

st.subheader("Opening Hours for Locations")
st.write(data[['description', 'opening_hours']])

# Step 2: Get Optimized Route
locations = [(row['latitude'], row['longitude']) for _, row in data.iterrows()]
optimized_route = get_optimized_route(locations, google_maps_api_key)

# Display the optimized route (order of locations to visit)
st.subheader("Optimized Route to Visit Locations")
if optimized_route:
    optimized_order = []
    for loc in optimized_route:
        lat, lng = loc['lat'], loc['lng']
        place = data.loc[(data['latitude'] == lat) & (data['longitude'] == lng), 'description'].values[0]
        optimized_order.append(place)
    
    st.write("Visit the locations in the following order:")
    st.write(" -> ".join(optimized_order))
else:
    st.write("No optimized route found. Please try again.")

# Create the map with markers and optimized route
if not data.empty:
    m = folium.Map(location=[data.iloc[0]['latitude'], data.iloc[0]['longitude']], zoom_start=10)
    
    # Add markers to Folium map
    for _, row in data.iterrows():
        marker_color = color_map.get(row.get('type', 'Default'), "gray")
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['description']} - {row['opening_hours']}",
            tooltip="Click for details",
            icon=folium.Icon(color=marker_color, icon_size=(30, 30))  # Increase the size of the pins
        ).add_to(m)

    # Display the optimized route (on the map as a polyline)
    if optimized_route:
        optimized_route_coords = [(loc['lat'], loc['lng']) for loc in optimized_route]
        folium.PolyLine(optimized_route_coords, color='blue', weight=5, opacity=0.7).add_to(m)
    
    # Display the Folium map
    folium_static(m)

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
