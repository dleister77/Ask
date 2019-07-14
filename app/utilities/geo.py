from flask import current_app
from geocodio import GeocodioClient
from geopy import distance
from threading import Thread

def _get_client():
    client = GeocodioClient(current_app.config['GEOCODIO_API_KEY'])
    return client

def geocode(address):
    """Get coordinates from Geocodio based on input address.
    Inputs:
        Address: based on geocodio format.
    Returns latitude and longitude as tuple
    """
    try:
        client = _get_client()
        location = client.geocode(address)
    except Exception as e:
        print(e)
        raise
    return location.coords

def get_distance(origin, destination):
    """Return geodesic distance between 2 points.
    origin: starting point expressed as latitude/longitude tuple
    destination: endingpoint expressed as latitude/longitude tuple
    """
    calculated_distance = distance.distance(origin, destination).miles
    return calculated_distance
    
def get_geo_range(origin, range):
    """Get lat and long max and min based on starting point and range."""
    range = distance.distance(miles=range)
    max_long = range.destination(origin, 90).longitude
    min_long = range.destination(origin, 270).longitude
    min_lat = range.destination(origin, 180).latitude
    max_lat = range.destination(origin, 000).latitude
    return (min_long, max_long, min_lat, max_lat)

