from collections import namedtuple
from datetime import date
import math
import os
from pathlib import Path
from shutil import rmtree
import threading
import time

from flask import url_for, current_app
from flask_login import current_user
from geocodio import GeocodioClient
from geocodio.exceptions import GeocodioAuthError
import pytest
from sqlalchemy.orm import sessionmaker
from werkzeug.datastructures import FileStorage

from app import create_app
from app import db
from app.models import User, Address, State, Category, Group, Provider, Review,\
                       FriendRequest, GroupRequest, addressTuple, Sector, Picture,\
                       Message, Message_User
import app.utilities.geo as geo
from app.utilities.geo import AddressError, APIAuthorizationError, _geocodeGEOCODIO
from app.utilities.helpers import thumbnail_from_buffer
from config import TestConfig

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

Session = sessionmaker()


def login(client, username, password):
    return client.post('/login', data=dict(username=username, 
                       password=password), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def scenarioUpdate(testCase, parameters, values, assertions):
    """"Update testCase for update scenario
    testCase: base test case
    parameters: parameter(dict key) to be updated.  single value or list.
    values: updated values parameter values.  single value or list of values if
            multiple parameters being updated.
    assertions: list of assertions to be updated. single list or list of lists.
    """
    for key, base_value in testCase.items():
        testCase[key] = (base_value, None)
    if parameters is None:
        pass
    elif type(parameters) == list:
        for param, val, assertion in zip(parameters, values, assertions):
            testCase[param] = (val, assertion)
    else:
        testCase[parameters] = (values, assertions)

def assertEqualsTolerance(testValue, targetValue, tolerance):
    tolerance = math.pow(10,-tolerance)
    lowerBounds = targetValue - tolerance
    upperBounds = targetValue + tolerance
    assert lowerBounds <= testValue <= upperBounds

@pytest.mark.usefixtures("dbSession")
class FunctionalTest(object):
    """Functional test base class.
    
    Attributes:
        routeFunction (str): Flask route function name (input to url_for)
        form (dict): test_case form arguments
    
    Methods:
        getRequest: helper method for test_client get requests
        postRequest: helper function for test_client post requests
    """

    routeFunction = None
    form = None

    def getRequest(self, client, *args, headers=None, **kwargs):
        """Return response from password reset request"""
        return client.get(url_for(self.routeFunction, *args, **kwargs, _external=False), 
                            follow_redirects=True, headers=headers)
    
    
    def postRequest(self, client, **kwargs):
        """Return response from password reset request"""
        return client.post(url_for(self.routeFunction, **kwargs,
                                            _external=False), 
                            data=self.form, follow_redirects=True)    

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

def start_app(*args, **kwargs):
    app = create_app(TestConfig)
    app.run()

@pytest.fixture(scope='session')
def testClient(app):
    client = app.test_client()
    yield client


@pytest.fixture(scope='function')
def activeClient(testClient, test_db):
    with testClient:
        login(testClient, TestConfig.TEST_USER['username'],
              TestConfig.TEST_USER['password']
              )
        yield testClient
        logout(testClient)


@pytest.fixture(scope='session')
def test_db(app):
    db.drop_all()
    db.create_all()
    #define categories
    s1 = State.create(id=1, name="North Carolina", state_short="NC")
    s2 = State.create(id=2, name="New York", state_short="NY")
    sect1 = Sector.create(id=1, name="Home Services")
    sect2 = Sector.create(id=2, name="Food & Drink")
    c1 = Category.create(id=1, name="Electrician", sector_id=1)
    c2 = Category.create(id=2, name="Plumber", sector_id=1)
    c3 = Category.create(id=3, name="Mexican Restaurant", sector_id=2)
    a1 = Address.create(line1="13 Brook St", city="Lakewood",
                        zip="14750", state_id = 2,
                        latitude=42.100201, longitude=-79.340303)

    #add test users
    u1 = User.create(id=1, username="sarahsmith", first_name="Sarah", last_name="Smith", 
             email="sarahsmith@yahoo.com",
             address = a1)
    u2 = User.create(id=2, username="jjones", first_name="John", last_name="Jones", 
             email="jjones@yahoo.com",
             address=Address(line1="7708 covey chase Dr", line2='', city="Charlotte",
                             zip="28210", state_id=1, latitude=35.123949,
                             longitude=-80.864783))
    u3 = User.create(id=3, username="yardsmith", first_name="Mark", last_name="Johnson",
              email="yardsmith@gmail.com",
              address=Address(line1="7718 Covey Chase Dr", line2='', city="Charlotte",
                              zip="28210", state_id=1, latitude=35.123681,
                             longitude=-80.865045)) 
    u4 = User.create(id=4, username="nukepower4ever", first_name="Hyman",
              last_name="Rickover", email="hyman@navy.mil",
              address=Address(line1="7920 Covey Chase Dr", line2='', city="Charlotte",
                              zip="28210", state_id=1, latitude=35.120759,
                             longitude=-80.865781))
    

    # add test providers
    p1 = Provider.create(id=1, name="Douthit Electrical", telephone="704-726-3329",
                  email="douthit@gmail.com", website='https://www.douthitelectrical.com/',
                  address=Address(line1="6000 Fairview Rd", line2="suite 1200",
                                  city="Charlotte", zip="28210", state_id=1,
                                  latitude=35.150495, longitude=-80.838958),
                  categories=[c1, c2])
    p2 = Provider.create(id=2, name="Evers Electric", telephone="7048431910",
                  email='', website='http://www.everselectric.com/',
                  address=Address(line1="3924 Cassidy Drive", line2="",
                                  city="Waxhaw", zip="28173", state_id=1,
                                  latitude=34.938645, longitude=-80.760691),
                  categories=[c1]),
    p3 = Provider.create(id=3, name="Preferred Electric Co", telephone="7043470446",
                         email="preferred@gmail.com", categories=[c1],
                  address=Address(line1="4113 Yancey Rd", line2='', city="charlotte",
                                  zip="28217", state_id=1, latitude=35.186947,
                                  longitude=-80.880459))

    #add test groups
    g1 = Group.create(id=1, name="QHIV HOA", description="Hoa for the neighborhood", admin_id=2)
    g2 = Group.create(id=2, name="Shannon's Bees", description="Insects that like to make honey", admin_id=2)
    g3 = Group.create(id=3, name="Shawshank Redemption Fans", description="test", admin_id=3)

    # add test reviews
    r1 = Review.create(id=1, user=u2, provider=p1, category=c1, rating=3, cost=3,
     description="fixed a light bulb", comments="satisfactory work.",
     pictures=[Picture(path=os.path.join(app.config['MEDIA_FOLDER'], '2', 'test1.jpg'), name='test1.jpg')])
    r2 = Review.create(id=2, user=u3, provider=p1, category=c1, rating=5, cost=5, price_paid="", description="installed breaker Box", comments="very clean")
    r3 = Review.create(id=3, user=u1, provider=p1, category=c1, rating=1, cost=5, price_paid="", description="test", comments="Test")
    r4 = Review.create(id=4, user=u2, provider=p3, category=c1, rating=5, cost=2, price_paid="", description="test", comments="Test123", service_date=date(2019, 5, 1))
    r5 = Review.create(id=5, user=u2, provider=p3, category=c1, rating=4, cost=3, price_paid="", description="moretest", comments="Test123456", service_date=date(2019, 5, 1))
    r6 = Review.create(id=6, user=u1, provider=p1, category=c1, rating=1, cost=5, price_paid="", description="yetanothertest", comments="Testing")

    # add test relationships
    u2.add(u1)
    u2.add(g1)
    u3.add(g1)

    # set user passwords
    u1.set_password("password1234")
    u2.set_password("password")
    u3.set_password("password5678")


    # set starting messages
    m1 = Message.send_new(dict(user_id=1), dict(user_id=2), "test subject", "test body")
    time.sleep(1)
    m2 = Message.send_new(dict(user_id=2), dict(full_name="admin"),"test admin subject", "test adminbody", msg_type="admin")
    m3 = Message.send_new(dict(user_id=1), dict(user_id=2), "yet another test subject", " yet another test body")

    yield db

    db.session.remove()
    db.drop_all()

@pytest.fixture(scope='function')
def dbSession(test_db):
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options)
    db.session = session
    yield session
    db.session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def testUser(dbSession):
    u1 = User.query.get(2)
    return u1

@pytest.fixture()
def testUser2(dbSession):
    u2 = User.query.get(1)
    return u2

@pytest.fixture()
def testUser3(dbSession):
    u3 = User.query.get(3)
    return u3

@pytest.fixture()
def testUser4(dbSession):
    u4 = User.query.get(4)
    return u4

@pytest.fixture()
def testProvider1(dbSession):
    p = Provider.query.get(1)
    return p

@pytest.fixture()
def testFriendrequest(dbSession, testUser, testUser4):
    request = FriendRequest.create(friend_id=testUser.id,
                                   requestor_id=testUser4.id)
    return request

@pytest.fixture()
def testFriendrequest2(dbSession, testUser, testUser3):
    request = FriendRequest.create(friend_id=testUser.id,
                                   requestor_id=testUser3.id)
    return request

@pytest.fixture()
def testGroup(dbSession):
    return Group.query.get(1)

@pytest.fixture()
def testGroup2(dbSession):
    return Group.query.get(2)

@pytest.fixture()
def testGroup3(dbSession):
    return Group.query.get(3)

@pytest.fixture()
def testGroupRequest(dbSession, testUser4, testGroup):
    request = GroupRequest.create(id=1, group_id=testGroup.id, requestor_id=testUser4.id)
    return request

@pytest.fixture()
def testGroupRequest2(dbSession, testUser4, testGroup3):
    request = GroupRequest.create(id=2, group_id=testGroup3.id, requestor_id=testUser4.id)
    return request

@pytest.fixture()
def testProvider(dbSession):
    return Provider.query.get(1)

@pytest.fixture()
def testAddress():
    address = addressTuple("8012 Covey Chase Dr", "Charlotte",
                           "NC", "28210")
    return address
    
@pytest.fixture()
def testReview(dbSession):
    return Review.query.get(1)

@pytest.fixture(scope='function')
def testPicture(activeClient):
    #named tuples to mock form
    form = namedtuple('form', ['picture', 'deletePictures'])
    picture = namedtuple('picture', 'data')
    deletePictures = namedtuple('deletePictures', 'data')
    filename = "test1.jpg"
    p = os.path.join(current_app.config['MEDIA_FOLDER'], 'source', filename)
    f = open(p, 'rb')
    fs = FileStorage(stream=f, filename=filename, content_type='image/jpeg')
    testform = form(picture([fs]), None)
    Picture.savePictures(testform)
    path = Path(os.path.join(current_app.config['MEDIA_FOLDER'],
                    str(current_user.id), filename))
    yield path
    try:
        rmtree(path.parent)
    except FileNotFoundError:
        raise

@pytest.fixture()
def test_recipient(dbSession):
    r = Message_User.query.filter_by(role="recipient").first()
    return r

@pytest.fixture()
def test_sender(dbSession):
    s = Message_User.query.filter_by(role="sender").first()
    return s

@pytest.fixture()
def test_message(dbSession):
    m = Message.query.get(1)
    return m

@pytest.fixture()
def search_form(app, dbSession):
    with app.app_context():
        from app.main.forms import ProviderSearchForm
        form = ProviderSearchForm()
        c = Category.query.filter_by(name="Electrician").first().id
        s = State.query.filter_by(name="North Carolina").first().id
        form.category.data = c
        form.state.data = s
        form.city.data = "Charlotte"
        yield form


@pytest.fixture()
def baseAddress():
    testCase = {"line1": "13 Brook St", "city": "Lakewood", "state": "2",
                 "zip": "14750"}
    return testCase

@pytest.fixture()
def newAddressDict():
    testCase = {"unknown": False, "line1": "13 Brook St", "line2":'', 
                "city": "Lakewood", "state_id": 2, "zip": "14750", "user_id": 4}
    return testCase

@pytest.fixture()
def baseLogin():
    testCase = {"username": "jjones", "password": "password"}
    return testCase

@pytest.fixture()
def newUserDict():
    testCase = {"first_name": "Roberto", "last_name": "Firmino",
                 "email": "rfirmino@lfc.com", "username": "rfirmino"}
    return testCase

@pytest.fixture()
def newProviderDict():
    addressDict = {"line1": "7708 Covey Chase Dr", 'line2': '',
                 "city": "Charlotte", "state": State.query.get(1),
                 "zip": "28210", "unknown": False}
    address = Address(**addressDict)
    testCase = {"name": "Smith Electric","telephone": "704-410-3873",
    "email": "smith@smith.com", "address": Address(**addressDict),
    "categories": [Category.query.get(1), Category.query.get(2)]}
    return testCase

@pytest.fixture()
def baseUserNew():
    testCase = {"first_name": "Roberto", "last_name":"Firmino",
                 "email": "rfirmino@lfc.com", "username": "rfirmino",
                 "password": "password", "confirmation": "password",
                 "address-line1": "13 Brook St", "address-city": "Lakewood",
                 "address-state": "2", "address-zip": "14750",
                 "address-line2": ''}
    return testCase


@pytest.fixture()
def baseUserNewForm():
    testCase = {"first_name": "Roberto", "last_name": "Firmino",
                 "email": "rfirmino@lfc.com", "username": "rfirmino",
                 "password": "password", "confirmation": "password",
                 "address-line1": "13 Brook St", "address-city": "Lakewood",
                 "address-state": "2", "address-zip": "14750"}
    return testCase

@pytest.fixture()
def base_user():
    testCase = {"first_name": "John", "last_name": "Jones",
                 "email": "jjones@yahoo.com", "username": "jjones",
                 "password": "password", "confirmation": "password",
                 "address": {"line1": "7708 Covey Chase Dr", 
                 "city": "Charlotte", "state": "1", "zip": "28210"}
                 }
    return testCase

@pytest.fixture()
def baseUser():
    testCase = {"first_name": "John", "last_name": "Jones",
                 "email": "jjones@yahoo.com", "username": "jjones",
                 "address-line1": "7708 Covey Chase Dr", 
                 "address-city": "Charlotte", "address-state": "1",
                 "address-zip": "28210"}
    return testCase

@pytest.fixture()
def baseFriendSearch():
    testCase = {"id": 3, "name": "Mark Johnson"}
    return testCase

@pytest.fixture()
def basePwUpdate():
    testCase = {"old": "password", "new": "passwordnew", "confirmation": 
				 "passwordnew"}
    return testCase


@pytest.fixture()
def baseReview():
    testCase = {"home": "home", "category": "1", "id": "2", "name": "Evers Electric",
                 "rating": "3", "cost": "3", "description": "test",
                 "service_date": "4/15/2019", "comments": "testcomments",
                 "picture": "", "certify": "True", "price_paid": "0"}
    return testCase

@pytest.fixture()
def baseReviewEdit(test_db):
    testReview = Review.query.get(1)
    test_case = {
			"id": str(testReview.id),
            "name": str(testReview.provider.name),
            "category": str(testReview.category_id),
            "rating": str(testReview.rating),
            "cost": str(testReview.cost),
            "price_paid": str(testReview.price_paid),
        	"description": str(testReview.description),
            "service_date": str(testReview.service_date),
			"comments": str(testReview.comments),
			"deletePictures" : ["1"],
			"certify": "True",
			"picture": ""
	}
    for k, v in test_case.items():
        if v == 'None':
            test_case[k] = ''
    return test_case

@pytest.fixture()
def newReviewDict():
    testCase = {"category": Category.query.get(1), "user": User.query.get(2),
                "provider": Provider.query.get(2),
                 "rating": "3", "cost": "3", "description": "test",
                 "service_date": "4/15/2019", "comments": "testcomments",
                 "pictures": []}
    return testCase

@pytest.fixture()
def baseProviderNew():
    """Return new provider that generates no validation errors."""
    testCase = {"sector": "1", "category": ["1","2"], "name": "Smith Electric",
                 "telephone": "704-410-3873", "website":'google.com', "email": "smith@smith.com",
                 "address-line1": "7708 Covey Chase Dr",
                 "address-city": "Charlotte", "address-state": 1,
                 "address-zip": "28210", "address-unknown": "False"}
    return testCase

@pytest.fixture()
def baseProviderSearch():
    testCase = {
        "location": 'home', "manual_location": "", "gpsLat": "",
        "gpsLong": "", "searchRange": 30, "sector": 1,  "category": 1, "name": None,
        "reviewed_filter": None, "friends_filter": None,
        "groups_filter": None, "sort": "name"
    }
    return testCase
 
@pytest.fixture()
def baseGroup():
    """Return existing group to be used for testing."""
    testCase = {"id": "2", "name": "Shannon's Bees",
                 "description": "Insects that like to make honey",
                 "admin_id": 2}
    return testCase

@pytest.fixture()
def baseGroupNew():
    """New group form inputs for testing."""
    testCase = {"name": "Porter's Pooches",
                 "description": "Dogs that like to swim in the creek.",
                 "admin_id": 2}
    return testCase

@pytest.fixture()
def baseGroupSearch():
    """Return group search form values for testing."""
    testCase = {"id": 3, "name": "Shawshank Redemption Fans"}
    return testCase

@pytest.fixture()
def baseMail():
    testCase = {"subject": "Test", 
                 "sender": TestConfig.ADMINS[0],
                 "recipients": ["test@test.com"],
                 "cc": ["test2@test.com"],
                 "text_body":"hello world!",
                 "html_body": "<p>hello world!<p>"}
    return testCase


@pytest.fixture()
def basePasswordReset():
    testCase = {"password_new": "password2",
                 "password_confirmation": "password2"}
    return testCase

@pytest.fixture()
def mockGeoResponse(monkeypatch):
    def mockGeoCode(address):
        # address = f"{address.line1}, {address.city}, {address.state} {address.zip}"
        if address == "1 Covey Chase Dr, Charlotte, NC 28210":
            raise AddressError
        else:
            return ((35.119714, -80.865332), address)
    
    monkeypatch.setattr('app.utilities.geo._geocodeGEOCODIO', mockGeoCode)

@pytest.fixture
def mockGeoApiBad(monkeypatch):
    def mockGeoCode(address):
        raise APIAuthorizationError
        
    monkeypatch.setattr('app.utilities.geo._geocodeGEOCODIO', mockGeoCode)

@pytest.fixture
def mockGeocodioApiBad(monkeypatch):
    def mockGeoCode():
        raise GeocodioAuthError
    
    monkeypatch.setattr('app.utilities.geo._get_client', mockGeoCode)

