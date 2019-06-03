from app import db
from app.models import User, Address, Group, Category, Review, Provider
from sqlalchemy.exc import IntegrityError
import pytest


def test_user(test_db):
    """
    GIVEN a User, Address model
    WHEN a new User is created
    THEN check the email, hashed_password, address, are set correctly.
    """
    u = User.query.filter_by(username="jjones").first()
    assert u.username == "jjones"
    assert u.email == "jjones@yahoo.com"
    assert u.password_hash != "shithead"
    assert u.check_password("password") == True
    assert u.check_password("liverpoolfc") == False
    assert u.address.line1 == "7708 Covey Chase Dr"
    assert u.address.city == "Charlotte"
    assert u.address.city != "charlotte"
    assert u.address.state.name == "North Carolina"
    assert u.summary()[0] == 3
    assert u.summary()[1] == 2

def test_relationships(test_db):
    """
    GIVEN a User, Group Model and Association Tables
    WHEN a new relationship is create
    THEN that group and friendships are established correctly
    """
    u = User.query.filter_by(username="jjones").first()
    f = User.query.filter_by(username="sarahsmith").first()
    nf = User.query.filter_by(username="yardsmith").first()
    g = Group.query.filter_by(name="Qhiv Hoa").first()
    assert f in u.friends
    assert g in u.groups
    assert nf not in u.friends
    assert u in f.friends
    assert u in g.members

def test_provider(test_db):
    """
    GIVEN a Provider model
    WHEN Provider added to db
    Then check name, categories, contact information
    """
    p = Provider.query.filter_by(id=1).first()
    c = Category.query.filter_by(name="Electrician").first()
    c2 = Category.query.filter_by(name="Plumber").first()
    assert p.name != "douthit electrical"
    assert p.name == "Douthit Electrical"
    assert p.telephone == "7047263329"
    assert p.email == "douthit@gmail.com"
    assert c in p.categories
    assert c2 not in p.categories
    assert p.profile()[2] == 3
    assert p.profile()[1] == 3
    assert p.profile()[0] == p
    assert p.profile_reviews().first().rating == 3

def test_user_update(test_db):
    """
    GIVEN User model
    WHEN User is updated
    CHECK ability to change name, address, and ability to detect duplicate
    email addresses and usernames
    """
    u = User.query.filter_by(username="jjones").first()
    u.update(username="jjones1", email="jjones1@gmail.com")
    u.address.update(line1="7000 covey Chase dr")
    db.session.commit()
    assert u.username == "jjones1"
    assert u.username != "jjones"
    assert u.email == "jjones1@gmail.com"
    assert u.address.line1 == "7000 Covey Chase Dr"
    with pytest.raises(IntegrityError):
        u.update(username="yardsmith")
        db.session.commit()
    db.session.rollback()
    with pytest.raises(IntegrityError):
        u.update(email="sarahsmith@yahoo.com")
        db.session.commit()
    db.session.rollback()

def test_user_search_reviews(test_db, search_form):
    """
    GIVEN User Model, search criteria
    WHEN User searches and filters by groups or friends
    CHECK returned reviews and summarized ratings
    """
    u = User.query.filter_by(username="jjones").first()
    #test average and count and return provider
    providers = u.search_providers(search_form).all()
    assert providers[0][1] == 3
    assert providers[0][2] == 3
    assert providers[0][0].name == "Douthit Electrical"
    #test casing on cities
    search_form.city.data = 'charlotte'
    providers = u.search_providers(search_form).all()
    assert providers[0][0].name == "Douthit Electrical"
    # test for filtering of groups_only
    search_form.groups_only.data = True
    providers = u.search_providers(search_form).all()
    assert providers[0][1] == 5
    assert providers[0][2] == 1
    # test for filtering of friends_only
    search_form.friends_only.data = True
    search_form.groups_only.data = False
    providers = u.search_providers(search_form).all()
    assert providers[0][1] == 1
    assert providers[0][2] == 1



    
    


    
    






