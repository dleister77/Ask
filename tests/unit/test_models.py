from app import db, mail
from app.helpers import dbUpdate
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
    assert u.check_password("password") is True
    assert u.check_password("liverpoolfc") is False
    assert u.address.line1 == "7708 Covey Chase Dr"
    assert u.address.city == "Charlotte"
    assert u.address.city != "charlotte"
    assert u.address.state.name == "North Carolina"
    assert u.summary()[0] == 3
    assert u.summary()[1] == 2
    assert u.email_verified is False


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

def test_provider(test_db, active_client):
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
    assert p.telephone != "704-726-3329"
    assert p.email == "douthit@gmail.com"
    assert c in p.categories
    assert c2 not in p.categories
    filter = {"friends_only": False, "groups_only": False}
    assert p.profile_reviews(filter).first().rating == 3
    assert p.profile(filter)[2] == 3
    assert p.profile(filter)[1] == 3
    assert p.profile(filter)[0] == p
    filter['friends_only'] = True
    assert p.profile_reviews(filter).first().rating == 1
    assert p.profile(filter)[2] == 1
    assert p.profile(filter)[1] == 1
    filter = {"friends_only": False, "groups_only": True}
    assert p.profile_reviews(filter).first().comments == "Very clean"
    assert p.profile(filter)[2] == 1
    assert p.profile(filter)[1] == 5

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
    dbUpdate()
    assert u.username == "jjones1"
    assert u.username != "jjones"
    assert u.email == "jjones1@gmail.com"
    assert u.address.line1 == "7000 Covey Chase Dr"
    with pytest.raises(IntegrityError):
        u.update(username="yardsmith")
        dbUpdate()
    with pytest.raises(IntegrityError):
        u.update(email="sarahsmith@yahoo.com")
        dbUpdate()
 

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


def test_user_pwd_tokens(test_app, test_db, base_user):
    """Test pwd reset token generation and verification."""
    test_user = User.query.filter_by(username=base_user['username']).first()
    alt_user = User.query.get(1)
    with mail.record_messages() as outbox:
        # test matched tokens
        t = test_user.get_reset_password_token()
        u = User.verify_password_reset_token(t)
        assert u == test_user
        # test mismatched tokens
        t2 = alt_user.get_reset_password_token()
        u = User.verify_password_reset_token(t2)
        assert u == alt_user
        assert u != test_user

def test_send_pswd_reset(test_app, test_db, base_user):
    """Test sending of password reset emails."""
    test_user = User.query.filter_by(username=base_user['username']).first()
    with mail.record_messages() as outbox:
        test_user.send_password_reset_email()
        t = test_user.get_reset_password_token()
        assert len(outbox) == 1
        msg = outbox[0]
        assert "jjones@yahoo.com" in msg.recipients
        assert msg.subject == 'Ask a Neighbor: Password Reset'
        assert 'To reset your password, please paste the below link into your browser' in msg.body

def test_send_email_verification(test_app, test_db, base_user):     
    """Test sending of email verification emails."""
    test_user = User.query.filter_by(username=base_user['username']).first()
    with mail.record_messages() as outbox:
        test_user.send_email_verification()
        assert len(outbox) == 1
        msg = outbox[0]
        assert "jjones@yahoo.com" in msg.recipients
        assert msg.subject == 'Ask a Neighbor: Email Verification'
        assert 'To verify your email' in msg.body
        assert 'Dear John' in msg.body

def test_verify_email_token(test_app, test_db, base_user):
    """Test verification of email tokens along with error codes."""
    test_user = User.query.filter_by(username=base_user['username']).first()
    test_token = test_user.get_email_verification_token()
    resulting_user, error = User.verify_email_verification_token(test_token)
    assert resulting_user == test_user
    assert error == None
    # check expired token
    test_token = test_user.get_email_verification_token(expires_in=-200)
    resulting_user, error = User.verify_email_verification_token(test_token)
    assert resulting_user == None
    assert error == "Expired"
    test_token = "xjdkldfj1893.xdkld.jfkdl"
    resulting_user, error = User.verify_email_verification_token(test_token)
    assert resulting_user == None
    assert error == "Invalid"   

    


    
    






