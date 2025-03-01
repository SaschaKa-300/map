import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium

st.title("Custom Map with Your Data")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

def load_data(file):
    df = pd.read_csv(file)
    return df

if uploaded_file is not None:
    data = load_data(uploaded_file)
    st.write("Preview of uploaded data:")
    st.dataframe(data.head())
    
    # Ensure required columns exist
    if {'latitude', 'longitude'}.issubset(data.columns):
        # Create map centered at the first data point
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
        st.error("CSV must contain 'latitude' and 'longitude' columns.")
