from app import create_app
from app import db
from app.models import User, Address, State, Category, Group, Provider, Review
from config import Config, basedir
from datetime import date
import os
import pytest

def login(client, username, password):
    return client.post('/login', data=dict(username=username, 
                       password=password), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

class TestConfig(Config):
    TESTING = True
    SERVER_NAME = 'localhost.localdomain'
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TEST_STATES = [(2, "New York"),(1, "North Carolina")]
    TEST_CATEGORIES = [(1, "Electrician"), (2, "Plumber")]
    TEST_USER = {"username": "jjones", "password": "password"}
    WTF_CSRF_ENABLED = False
    MEDIA_FOLDER = os.path.join(basedir, 'instance', 'tests', 'photos')
    REVIEWS_PER_PAGE = 1


@pytest.fixture(scope='module')
def test_app():
    app = create_app(TestConfig)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture(scope='module')
def test_client(test_app):
    client = test_app.test_client()
    yield client

@pytest.fixture(scope='function')
def active_client(test_client, test_db):
    with test_client:
        login(test_client, "jjones", "password")
        # login(test_client, TestConfig['TEST_USER']['username'], TestConfig['TEST_USER']['password'])
        yield test_client

@pytest.fixture()
def test_db(test_app):
    db.create_all()
    #define categories
    s1 = State(name="North Carolina", state_short="NC")
    s2 = State(name="New York", state_short="NY")
    c1 = Category(name="Electrician")
    c2 = Category(name="Plumber")

    #add test addresses
    a1 = Address(line1="13 Brook St", city="Lakewood", zip="14750", state=s2)
    a2 = Address(line1="7708 covey chase Dr", city="Charlotte", zip="28210", 
                state=s1)
    a3 = Address(line1="7706 Covey Chase Dr", city="Charlotte", zip="28210",
                 state=s1)
    a4 = Address(line1="6000 Fairview Rd", line2="suite 1200", city="Charlotte",
                 zip="28210", state=s1)
    a5 = Address(line1="3924 Cassidy Drive", line2="", city="Waxhaw", zip="28173",
                 state=s1)
    a6 = Address(line1="4113 Yancey Rd", city="charlotte", zip="28217", 
                 state=s1)


    #add test users
    u1 = User(id=1, username="sarahsmith", first_name="Sarah", last_name="Smith", 
             email="sarahsmith@yahoo.com", address=a1)
    u1.set_password("password1234")
    u2 = User(id=2, username="jjones", first_name="John", last_name="Jones", 
             email="jjones@yahoo.com", address=a2)
    u2.set_password("password")
    u3 = User(id=3, username="yardsmith", first_name="Mark", last_name="Johnson",
              email="yardsmith@gmail.com", address=a3)
    u4 = User(id=4, username="nukepower4ever", first_name="Hyman", last_name="Rickover",
              email="hyman@navy.mil", address=a4)
    
    #add test groups
    g1 = Group(id=1, name="QHIV HOA", description="Hoa for the neighborhood", admin_id=1)
    g2 = Group(id=2, name="Shannon's Bees", description="Insects that like to make honey", admin_id=1)
    g3 = Group(id=3, name="Shawshank Redemption Fans", description="test", admin_id=1)
    # add test relationships
    u2.add(u1)
    u2.add(g1)
    u3.add(g1)

    # add test providers
    p1 = Provider(id=1, name="douthit electrical", telephone="704-726-3329",
                  email="douthit@gmail.com", address=a4, categories=[c1])
    p2 = Provider(id=2, name="Evers Electric", telephone="7048431910",
                  address=a5, categories=[c1])
    p3 = Provider(id=3, name="Preferred Electric Co", telephone="7043470446",
                  address=a6, categories=[c1])

    # add test reviews
    r1 = Review(user=u2, provider=p1, category=c1, rating=3, description="fIxed A light BULB", comments="satisfactory work.")
    r2 = Review(user=u3, provider=p1, category=c1, rating=5, description="installed breaker Box", comments="very clean")
    r3 = Review(user=u1, provider=p1, category=c1, rating=1, description="test", comments="Test")
    r4 = Review(user=u2, provider=p3, category=c1, rating=3, description="test", comments="Test123", service_date=date(2019, 5, 1))
    db.session.add_all([c1, c2, a1, a2, a3, a4, a5, u1, u2, u3, u4, g1, g2, g3, p1, p2, p3, r1, r2, r3, r4])
    db.session.commit()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture()
def search_form(test_app, test_db):
    with test_app.app_context():
        from app.main.forms import ProviderSearchForm
        form = ProviderSearchForm()
        c = Category.query.filter_by(name="Electrician").first().id
        s = State.query.filter_by(name="North Carolina").first().id
        form.category.data = c
        form.state.data = s
        form.city.data = "Charlotte"
        yield form


@pytest.fixture()
def base_address():
    test_case = {"line1": "13 Brook St", "city": "Lakewood", "state": "2", "zip": "14750"}
    return test_case

@pytest.fixture()
def base_login():
    test_case = {"username": "jjones", "password": "password"}
    return test_case


@pytest.fixture()
def base_user_new():
    test_case = {"first_name": "Roberto", "last_name": "Firmino",
                 "email": "rfirmino@lfc.com", "username": "rfirmino",
                 "password": "password", "confirmation": "password",
                  "address": {"line1": "13 Brook St", 
						 "city": "Lakewood", "state": "2", "zip": "14750"}
                 }
    return test_case

@pytest.fixture()
def base_user():
    test_case = {"first_name": "John", "last_name": "Jones",
                 "email": "jjones@yahoo.com", "username": "jjones",
                 "password": "password", "confirmation": "password",
                  "address": {"line1": "7708 Covey Chase Dr", 
                  "city": "Charlotte", "state": "1", "zip": "28210"}
                 }
    return test_case

@pytest.fixture()
def base_pw_update():
    test_case = {"old": "password", "new": "passwordnew", "confirmation": 
				"passwordnew"}
    return test_case

@pytest.fixture()
def base_review():
    test_case = {"category": "1", "name": "2",
                 "rating": "3", "service_description": "test",
                 "service_date": "4/15/2019", "comments": "testcomments"}
    return test_case

@pytest.fixture()
def base_provider_new():
    """Return new provider that generates no validation errors."""
    test_case = {"category": ["1", "2"], "name": "Smith Electric",
                "telephone": "704-410-3873", "email": "smith@smith.com",
                "address": {"line1": "7708 Covey Chase Dr", 
						   "city": "Charlotte", "state": 1, "zip": "28210"}
				}
    return test_case

