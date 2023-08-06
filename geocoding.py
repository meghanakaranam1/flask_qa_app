# geocoding.py

import requests
import os

GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'  # Replace this with your actual API key

def get_latitude_longitude(location):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': location,
        'key': GOOGLE_MAPS_API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        results = data['results']
        if results:
            geometry = results[0]['geometry']
            location_info = geometry['location']
            return location_info['lat'], location_info['lng']
    return None, None
