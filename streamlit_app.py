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

# Function to get optimized route and directions from Google Directions API
def get_directions(locations, api_key):
    origin = f"{locations[0][0]},{locations[0][1]}"
    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:]])
    destination = origin  # Assume round-trip
    
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints=optimize:true|{waypoints}&key={api_key}"
    response = requests.get(directions_url).json()
    
    if response['status'] == 'OK':
        route = response['routes'][0]
        optimized_order = route['waypoint_order']  # Optimized order of locations
        steps = []
        polyline_points = route['overview_polyline']['points']
        
        for leg in route['legs']:
            for step in leg['steps']:
                instructions = step['html_instructions']  # HTML-formatted instructions
                distance = step['distance']['text']
                duration = step['duration']['text']
                steps.append(f"{html.unescape(instructions)} ({distance}, {duration})")
        
        return optimized_order, steps, polyline_points
    return [], [], ""

st.title("Custom Maps with Navigation")

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
    "Bestandskunde": "blue",
    "..": "orange"
}

if not data.empty:
    # Create a list of locations (latitude, longitude)
    locations = [(row['latitude'], row['longitude']) for _, row in data.iterrows()]
    
    # Get optimized route and directions
    optimized_order, steps, polyline_points = get_directions(locations, google_maps_api_key)
    
    # Create map centered at the first valid location
    m = folium.Map(location=[data.iloc[0]['latitude'], data.iloc[0]['longitude']], zoom_start=12)
    
    # Add markers in the optimized order
    for idx, loc_idx in enumerate(optimized_order):
        row = data.iloc[loc_idx]
        marker_color = color_map.get(row.get('type', 'Default'), "gray")
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['description']} - Stop {idx+1}",
            tooltip=f"Stop {idx+1}: {row['description']}",
            icon=folium.Icon(color=marker_color)
        ).add_to(m)

    # Add route polyline
    if polyline_points:
        folium.PolyLine(locations, color="blue", weight=5, opacity=0.7).add_to(m)

    # Display the Folium map
    folium_static(m)
    
    # Display navigation instructions
    st.subheader("Step-by-Step Navigation Instructions")
    for i, step in enumerate(steps):
        st.markdown(f"**Step {i+1}:** {step}")

    # Embed a Google Map with route visualization
    st.subheader("Google Maps View")
    map_center = f"{data.iloc[0]['latitude']}, {data.iloc[0]['longitude']}"
    
    # Generate markers for Google Maps
    google_markers = "".join([
        f"""
        var marker{idx} = new google.maps.Marker({{
            position: new google.maps.LatLng({row['latitude']}, {row['longitude']}),
            map: map,
            icon: 'http://maps.google.com/mapfiles/ms/icons/{color_map.get(row.get('type', 'Default'), 'gray')}-dot.png'
        }});

        var infowindow{idx} = new google.maps.InfoWindow({{
            content: '<strong>Stop {idx+1}: {html.escape(row["description"])}</strong>'
        }});

        marker{idx}.addListener('click', function() {{
            infowindow{idx}.open(map, marker{idx});
        }});
        """
        for idx, row in data.iterrows()
    ])
    
    google_map_html = f"""
    <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}"></script>
    <div id="map" style="height: 500px; width: 100%;"></div>
    <script>
        function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 12,
                center: new google.maps.LatLng({map_center})
            }});
            {google_markers}

            var directionsService = new google.maps.DirectionsService();
            var directionsRenderer = new google.maps.DirectionsRenderer();
            directionsRenderer.setMap(map);
            
            var waypoints = [
                {",".join([f"{{ location: new google.maps.LatLng({lat}, {lng}), stopover: true }}" for lat, lng in locations[1:-1]])}
            ];
            
            var request = {{
                origin: new google.maps.LatLng({locations[0][0]}, {locations[0][1]}),
                destination: new google.maps.LatLng({locations[0][0]}, {locations[0][1]}),
                waypoints: waypoints,
                travelMode: 'DRIVING',
                optimizeWaypoints: true
            }};
            
            directionsService.route(request, function(result, status) {{
                if (status == 'OK') {{
                    directionsRenderer.setDirections(result);
                }}
            }});
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
