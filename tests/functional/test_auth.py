from app.models import State, User
from flask import escape, url_for
from flask_login import current_user
import pytest

def login(client, username, password):
    return client.post('/login', data=dict(username=username, 
                       password=password), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def register(client, form):
    return client.post('/register', data=form, follow_redirects=True)

def update(client, form):
    return client.post(url_for('auth.userupdate', _external=False), data=form,
                       follow_redirects=True)

def passwordUpdate(client, form):
    return client.post(url_for('auth.passwordupdate', _external=False),
                       data=form, follow_redirects=True)


def test_login(test_client, test_db):
    # test standard login
    response = login(test_client, 'jjones', 'password')
    assert response.status_code == 200
    assert b'Search for Provider' in response.data
    response = logout(test_client)
    assert response.data == test_client.get(url_for('auth.index', _external=False)).data
    # test for inability to access login required page
    check = test_client.get(url_for('main.review', _external=False), follow_redirects=True)
    assert b'Please log in to access the request page' in check.data
    # test invalid password
    response = login(test_client, 'jjones', 'password1234')
    assert b'Invalid username or password' in response.data
    response = logout(test_client)
    # test invalid username
    response = login(test_client, 'jjones1000', 'password')
    assert b'Invalid username or password' in response.data
    response = logout(test_client)
    response = login(test_client, 'jjones', None)
    assert b'Password is required.' in response.data
    response = logout(test_client)
    response = login(test_client, None, 'password')
    assert b'Username is required.' in response.data

def test_register(test_client, test_db):
    id = State.query.filter_by(name="North Carolina").first().id
    # register new user
    test_case = {'first_name': "Ted", 'last_name': "Robinson", 
                'address-line1': "2614 Roswell Ave", 'address-city': "Charlotte",
                'address-state': id, 'address-zip': "28209", 'email': "test@test.com",
                'username': "trobinson", 'password': "password", 
                'confirmation': "password"}
    response = register(test_client, test_case)
    assert response.status_code == 200
    check = escape("Congratulations! You've successfully registered")
    # check new user can log in
    assert bytes(check, encoding="ascii") in response.data
    response = login(test_client, username="trobinson", password="password")
    assert response.status_code == 200
    assert b'Search for Provider' in response.data
    response = logout(test_client)
    # test checks for registering user with existing username
    test_case.update({'first_name': "Tom", 'email': "test1@test.com"})
    response = register(test_client, test_case)
    assert b'Username is already registered' in response.data
    assert response.status_code == 200
    # test for existing email address
    test_case.update({'email': "test@test.com",'username': "tomrobinson"})
    response = register(test_client, test_case)
    assert b'Email address is already registered' in response.data
    # test for password mismatch
    test_case.update({'email': "test1@test.com", 'password': 'password1234'})
    response = register(test_client, test_case)
    assert b'Passwords must match' in response.data
    # test for password less than required length
    test_case.update({'password':'1234', 'confirmation': '1234'})
    response = register(test_client, test_case)
    assert b'Field must be between 7 and 15 characters long' in response.data
    # check for case of missing data from required field
    test_case.update({'password':'password', 'confirmation':'password',
                     'first_name': None})
    response = register(test_client, test_case)
    assert b'First name is required' in response.data


def test_userupdate(test_client, test_db):
    id = State.query.filter_by(name="North Carolina").first().id
    # successfully change name and address line1
    test_case = {'first_name': "John", 'last_name': "Johnson", 
            'address-line1': "7710 Covey Chase Dr", 'address-city': "Charlotte",
            'address-state': id, 'address-zip': "28210", 
            'email': "jjones@yahoo.com", 'username': "jjones"}
    login(test_client, "jjones", "password")
    response = update(test_client, test_case)
    assert response.status_code == 200
    assert b'John Johnson' in response.data
    assert b'User information updated' in response.data
    # change to email address already in use
    test_case.update({"email": "sarahsmith@yahoo.com"})
    response = update(test_client, test_case)
    assert b'Email address is already registered' in response.data
    # change to username that is already used
    test_case.update({"email": "jjones@yahoo.com", "username": "yardsmith"})
    response = update(test_client, test_case)
    assert b'Username is already registered' in response.data
    assert b'User information update failed' in response.data
    # remove required field
    test_case.update({"username": "jjones", "first_name": None})
    response = update(test_client, test_case)
    assert b'First name is required' in response.data

def test_passwordupdate(test_client, test_db):
    login(test_client, "jjones", "password")
    # change password and log back in
    test_case = {"old": "password", "new": "password1", "confirmation": "password1"}
    response = passwordUpdate(test_client, test_case)
    assert b'Password updated' in response.data
    # incorrect old password
    test_case = {"old": "password", "new": "password2", "confirmation": "password2"}
    response = passwordUpdate(test_client, test_case)
    assert b'Invalid password' in response.data
    assert b'Password update failed' in response.data
    # mismatch old and new passwords
    test_case = {"old": "password1", "new": "password2", "confirmation": "password3"}
    response = passwordUpdate(test_client, test_case)
    assert b'Passwords must match' in response.data
    assert b'Password update failed' in response.data
    # new password too short
    test_case = {"old": "password1", "new": "pass", "confirmation": "pass"}
    response = passwordUpdate(test_client, test_case)
    assert b'Field must be between 7 and 15 characters long' in response.data
    assert b'Password update failed' in response.data   