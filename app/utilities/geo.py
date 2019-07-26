from flask import current_app, g, session
from flask_login import current_user
from geocodio import GeocodioClient
from geopy import distance
from threading import Thread

def _get_client():
    client = GeocodioClient(current_app.config['GEOCODIO_API_KEY'])
    return client

def geocode(address):
    """Get coordinates from Geocodio based on input address.
    Args:
        Address (str): lookup address in format: 'line1, city, state'.
    
    Returns:
        tuple: lat/long coordintes and formatted address

    Raises:

    """
    try:
        client = _get_client()
        location = client.geocode(address)
    except Exception as e:
        print(e)
        raise
    return location.coords, location.formatted_address

def get_distance(origin, endpoint):
    """Return geodesic distance between 2 points.
    Args:
        origin (tuple): starting point expressed as latitude/longitude
        endpoint: ending point expressed as latitude/longitude
    Returns:
        float: geodesic distance in miles from origin to endpoint
    """
    calculated_distance = distance.distance(origin, endpoint).miles
    return calculated_distance
    
def get_geo_range(origin, range):
    """Get lat and long max and min based on starting point and range."""
    range = distance.distance(miles=range)
    max_long = range.destination(origin, 90).longitude
    min_long = range.destination(origin, 270).longitude
    min_lat = range.destination(origin, 180).latitude
    max_lat = range.destination(origin, 000).latitude
    return (min_lat, max_lat, min_long, max_long)

def sortByDistance(searchOrigin, toBeSorted):
        """Sort search results by geodesic distance from searchOrigin.

        Args:
           searchOrigin (tuple): lat/long starting point for
                                 distance calculations
           toBeSorted (list): list of objects/named tuples to be sorted by distance

        Returns:
           list (list): sorted by distance
        """

        toBeSorted.sort(key=lambda item: get_distance(searchOrigin,
                                         (item.latitude, item.longitude))
                       )
        return toBeSorted


class Location(object):
    """Consolidated geolocation data.

    Attributes:
        source (str): source of location, 'home', 'gps' or 'manual'
        address (str): street address associated w/ lat/long, '' for 'gps'
        coordinates (tuple): tuple containing latititude and longitude
        latitude (flt): latitude as float
        longitude (flt): longitude as float
        minLat (flt): min latitude for range calculation
        maxLat (flt): max latitude for range calcualtion
        minLong (flt): min longitude for range calculation
        maxLong (flt): max longitude for range calculation
        

    Methods:
       addToSession: Adds location source, coordinates and address to session
       setRangeCoordinates: Determines max/min lat/long to create range boundary
                            around Location lat/long
    """
    def __init__(self, source, address=None, coordinates=None):
        self.source = source
        self._address = address
        self.coordinates = coordinates
        self.latitude
        self.longitude
        self.minLat = None
        self.maxLat = None
        self.minLong = None
        self.maxLong = None
        self.addToSession()

    @property
    def coordinates(self):
        """Returns lat/long as a tuple and saves tuple coord as lat and long."""
        return (self.latitude, self.longitude)

    @coordinates.setter
    def coordinates(self, coordinates):
        if self.source == "gps":
            coordinates = coordinates
        elif self.source == "manual":
            coordinates, address = geocode(self.address)
            self._address = address
        elif self.source == "home":
            coordinates = current_user.address.coordinates
        elif self.source == "manualExisting":
            coordinates = session['location']['coordinates']
        self.latitude, self.longitude = coordinates

    @property
    def address(self):
        """Returns and sets _address.

        Returns and sets address.  Setter bases address off of location source.

        Args:
            address (str): optional, string of street address, city, and state.
                           only required if source is manual.
        """
        return self._address

    @address.setter
    def address(self, address):
        if self.source == "gps":
            self._address = ""
        if self.source == "manual":
            self._address = g.geoQuery
        if self.source == "home":
            self._address = f"{current_user.address.line1}, "\
                           f"{current_user.address.city}, "\
                           f"{current_user.address.state.state_short}"
            
    def addToSession(self):
        """Adds location source, coordinates and address to user session"""
        if self.source == "manualExisting":
            pass
        else:
            session['location'] = {"coordinates": self.coordinates, 
                                   "source": self.source,
                                   "address": self.address,
                                   "latitude": self.latitude,
                                   "longitude": self.longitude}
        return None

    def setRangeCoordinates(self, range=30):
        """Determines coordinates to create range box around Location.
        
        Based on a specified range, calculates min/max lat and long to create a
        box around the location lat/long.  Allows search within the range. Modifies 
        Args:
            range (int): optional, defaults to 30 miles.  
        
        Returns:
            self: 
        """
        bounds = get_geo_range(self.coordinates, range)
        self.minLat, self.maxLat, self.minLong, self.maxLong = bounds
        return self

    def __repr__(self):
        return f"<Location {self.latitude} {self.longitude}>"
    
    


