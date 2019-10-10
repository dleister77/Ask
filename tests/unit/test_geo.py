from collections import namedtuple

from flask import session
from geopy import distance
import pytest

from app.models import addressTuple
from app.utilities.geo import geocode, _geocodeGEOCODIO, _geocodeTamu, getGeoRange, getDistance,\
                              Location, sortByDistance, AddressError
from tests.conftest import assertEqualsTolerance

def test_geocode(test_app):
    address = "7708 Covey Chase Dr, Charlotte, NC 28210"
    location = geocode(address)
    assert location[0] == (35.123949, -80.864783)
    assert location[1] == "7708 Covey Chase Dr, Charlotte, NC 28210"

def test_geocodeInvalid(mockGeoResponse):
    address = "1 Covey Chase Dr, Charlotte, NC 28210"
    with pytest.raises(AddressError):
        location = geocode(address)


def test_geocodeGEOCODIO(test_app):
    address = "7708 Covey Chase Dr, Charlotte, NC 28210"
    location = _geocodeGEOCODIO(address)
    assert location[0] == (35.123949, -80.864783)
    assert location[1] == "7708 Covey Chase Dr, Charlotte, NC 28210"

def test_geocodeGEOCODIOInvalidAddress(test_app):
    with pytest.raises(AddressError):
        address = "1 covey chase dr charlotte nc"
        _geocodeGEOCODIO(address)
    with pytest.raises(AddressError):
        address = "7550 Covey Chase Dr Charlotte nc"
        _geocodeGEOCODIO(address)
        
def test_geocodeAuthError(test_app, mockGeoApiBad):
    address = "7708 Covey Chase Dr, Charlotte, NC 28210"
    location = geocode(address)
    assert location[0] == (35.123949, -80.864783)
    assert location[1] == "7708 Covey Chase Dr, Charlotte, NC 28210"

def test_geocodeGECODIOAuthError(test_app, mockGeocodioApiBad):
    address = "7708 Covey Chase Dr, Charlotte, NC 28210"
    location = geocode(address)
    assert location[0] == (35.123949, -80.864783)
    assert location[1] == "7708 Covey Chase Dr, Charlotte, NC 28210"

def test_getGeoRange():
    testOrigin = (35.123949, -80.864783)
    GeoRange = getGeoRange(testOrigin, 30)
    assert GeoRange == (34.68875146092123, 35.55911523212324,
                       -81.39445614485395, -80.33510985514606)
    assert round(getDistance(testOrigin, (testOrigin[0], GeoRange[2])),2) == 30
    assert round(getDistance(testOrigin, (testOrigin[0], GeoRange[3])),2) == 30
    assert round(getDistance(testOrigin, (GeoRange[0], testOrigin[1])),2) == 30
    assert round(getDistance(testOrigin, (GeoRange[1], testOrigin[1])),2) == 30

def test_sortByDistance():
    GeoPoint = namedtuple('GeoPoint', ['latitude', 'longitude'])
    testOrigin = GeoPoint(35.123949, -80.864783)
    testNear = GeoPoint(35.117352, -80.857002)
    testMedium = GeoPoint(35.174576, -80.848514)
    testMediumNear = GeoPoint(35.167525, -80.85078)
    testFar = GeoPoint(35.223903, -80.848642)
    testList = [testMedium, testFar, testMediumNear, testNear]
    sortedList = sortByDistance(testOrigin, testList)
    assert sortedList == [testNear, testMediumNear, testMedium, testFar]

def test_geocodeTamu(test_app):
    address = addressTuple('7708 Covey Chase Dr', 'Charlotte', 'NC', '28210')
    location = _geocodeTamu(address)
    assert location[0] == (35.123949, -80.864783)
    assert location[1] == "7708 Covey Chase Dr, Charlotte, NC 28210"


def test_LocationAddToSession(dbSession, activeClient):
    assert 'location' not in session
    location = Location("gps", "", (35.123949, -80.864783))
    session.pop('location')
    assert 'location' not in session
    location.addToSession()
    assert session['location']['source'] == "gps"
    assert session['location']['address'] == ""
    assert session['location']['coordinates'] == (35.123949, -80.864783)
    assert session['location']['latitude'] == 35.123949
    assert session['location']['longitude'] == -80.864783
    
def test_LocationNewGPS(dbSession, activeClient):
    location = Location("gps", "", (35.123949, -80.864783))
    assert location.source == "gps"
    assert location.address == ""
    assert location.coordinates == (35.123949, -80.864783)
    assert session['location']['source'] == "gps"
    assert session['location']['coordinates'] == (35.123949, -80.864783)

def test_LocationNewManual(dbSession, activeClient):
    location = Location("manual", "7708 Covey Chase Dr Charlotte, NC 28210")
    assert location.source == "manual"
    assert location.address == "7708 Covey Chase Dr, Charlotte, NC 28210"
    assert location.coordinates == (35.123949, -80.864783)
    assert session['location']['source'] == "manual"
    assert session['location']['address'] == "7708 Covey Chase Dr, Charlotte, NC 28210"

def test_LocationNewHome(dbSession, activeClient):
    location = Location("home")
    assertEqualsTolerance(location.latitude, 35.123949, 5)
    assertEqualsTolerance(location.longitude, -80.864783, 5)

def test_LocationSetRangeCoords(dbSession, activeClient, mockGeoResponse):
    location = Location("manual", "8012 Covey Chase Dr, Charlotte, NC 28210")
    location.setRangeCoordinates()
    distance1 = distance.distance(location.coordinates,
                                 (location.latitude, location.maxLong)).miles
    distance2 = distance.distance(location.coordinates,
                                 (location.latitude, location.minLong)).miles
    distance3 = distance.distance(location.coordinates,
                                 (location.maxLat, location.longitude)).miles
    distance4 = distance.distance(location.coordinates,
                                 (location.minLat, location.longitude)).miles                                                                      
    distanceList = [distance1, distance2, distance3, distance4]
    for d in distanceList:
        assert round(d,1) == 30.0