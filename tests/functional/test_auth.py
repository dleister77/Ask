from app.models import State, User
from flask import escape, session, url_for


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


def email_verify(client, token):
    """Return response from email verify route"""
    return client.get(url_for('auth.email_verify', token=token, _external=False), 
                      follow_redirects=True)


def email_verify_request(client):
    """Return response from email verify request"""
    return client.get(url_for('auth.email_verify_request', _external=False), 
                      follow_redirects=True)


def password_reset_request(client):
    """Return response from password reset request"""
    return client.get(url_for('auth.password_reset_request', _external=False), 
                      follow_redirects=True)


def password_reset_request_post(client, form):
    """Return response from password reset request"""
    return client.post(url_for('auth.password_reset_request', _external=False), 
                       data=form, follow_redirects=True)


def password_reset(client, token):
    """Return response from password reset route"""
    return client.get(url_for('auth.passwordreset', token=token, _external=False), 
                      follow_redirects=True)


def password_reset_post(client, token, form):
    """Return response from password reset post request"""
    return client.post(url_for('auth.passwordreset', token=token,
                              _external=False), 
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
    assert b'Please log in to access the requested page' in check.data
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

def test_register(test_client, test_db, base_user_new_form):
    # register new user
    test_case = base_user_new_form.copy()
    response = register(test_client, test_case)
    assert response.status_code == 200
    check = escape("Congratulations! You've successfully registered")
    # check new user can log in
    assert bytes(check, encoding="ascii") in response.data
    response = login(test_client, username=base_user_new_form['username'],
                     password=base_user_new_form['password'])
    assert response.status_code == 200
    assert b'Search for Provider' in response.data
    response = logout(test_client)
    # test checks for registering user with existing username
    test_case.update({'first_name': "Tom", 'email': "test1@test.com"})
    response = register(test_client, test_case)
    assert b'Username is already registered' in response.data
    assert response.status_code == 200
    # test for existing email address
    test_case.update({'email': base_user_new_form['email'],
                      'username': "allison"})
    response = register(test_client, test_case)
    assert b'Email address is already registered.' in response.data
    # test for password mismatch
    test_case.update({'email': "test1@test.com", 'password': 'password1234'})
    response = register(test_client, test_case)
    assert b'Passwords must match' in response.data
    # test for password less than required length
    test_case.update({'password': '1234', 'confirmation': '1234'})
    response = register(test_client, test_case)
    assert b'Field must be between 7 and 15 characters long' in response.data
    # check for case of missing data from required field
    test_case.update({'password': 'password', 'confirmation': 'password',
                     'first_name': None})
    response = register(test_client, test_case)
    assert b'First name is required' in response.data


def test_userupdate(active_client, test_db):
    id = State.query.filter_by(name="North Carolina").first().id
    # successfully change name and address line1
    test_case = {'first_name': "John", 'last_name': "Johnson", 
                 'address-line1': "7710 Covey Chase Dr",
                 'address-city': "Charlotte", 'address-state': id,
                 'address-zip': "28210", 'email': "jjones@yahoo.com",
                 'username': "jjones"}
    response = update(active_client, test_case)
    assert response.status_code == 200
    assert b'John Johnson' in response.data
    assert b'User information updated' in response.data
    # change to email address already in use
    test_case.update({"email": "sarahsmith@yahoo.com"})
    response = update(active_client, test_case)
    assert b'Email address is already registered' in response.data
    # change to username that is already used
    test_case.update({"email": "jjones@yahoo.com", "username": "yardsmith"})
    response = update(active_client, test_case)
    assert b'Username is already registered' in response.data
    assert b'User information update failed' in response.data
    # remove required field
    test_case.update({"username": "jjones", "first_name": None})
    response = update(active_client, test_case)
    assert b'First name is required' in response.data

def test_passwordupdate(active_client, test_db):
    # change password and log back in
    test_case = {"old": "password", "new": "password1", "confirmation": "password1"}
    response = passwordUpdate(active_client, test_case)
    assert b'Password updated' in response.data
    # incorrect old password
    test_case = {"old": "password", "new": "password2", "confirmation": "password2"}
    response = passwordUpdate(active_client, test_case)
    assert b'Invalid password' in response.data
    assert b'Password update failed' in response.data
    # mismatch old and new passwords
    test_case = {"old": "password1", "new": "password2", "confirmation": "password3"}
    response = passwordUpdate(active_client, test_case)
    assert b'Passwords must match' in response.data
    assert b'Password update failed' in response.data
    # new password too short
    test_case = {"old": "password1", "new": "pass", "confirmation": "pass"}
    response = passwordUpdate(active_client, test_case)
    assert b'Field must be between 7 and 15 characters long' in response.data
    assert b'Password update failed' in response.data

def test_email_verify(test_client, test_db, base_user):
    """Test route for verifying email reset_token."""
    test_user = User.query.filter_by(username=base_user['username']).first()
    test_token = test_user.get_email_verification_token()
    response = email_verify(test_client, test_token)
    assert b'Email successfully verified' in response.data
    assert response.status_code == 200
    test_token = test_user.get_email_verification_token(expires_in=-200)
    response = email_verify(test_client, test_token)
    assert b"Email verification failed due to expiration of verification code"\
           in response.data 


def test_email_verify_request(test_client, test_db, base_user):
    """Test route for email reset to be sent."""
    test_user = User.query.filter_by(username=base_user['username'])
    response = email_verify_request(test_client)
    assert b'Please log in to request a new email verification link.' in response.data
    login(test_client, base_user['username'], base_user['password'])
    with test_client as c:
        response = email_verify_request(c)
        assert b'Please check your email for an email verification message.' in response.data
        assert session['email_verification_sent'] == True


def test_password_reset_request(test_client, test_db, base_user):
    """Test route request password reset email to be sent."""
    response = password_reset_request(test_client)
    assert response.status_code == 200
    assert "<h3>Password Reset Request</h3>" in response.data.decode()
    test_case = {"email": base_user["email"]}
    response = password_reset_request_post(test_client, test_case)
    assert b"Check email for instructions to reset your password" in response.data


def test_password_reset_new(test_client, test_db, base_user,
                            base_password_reset):
    """Test actual resetting of password via password reset request."""
    test_user = User.query.filter_by(username=base_user['username']).first()
    test_token = test_user.get_reset_password_token()    
    # test get request
    response = password_reset(test_client, test_token)
    assert response.status_code == 200
    assert "<h3>Password Reset</h3>" in response.data.decode()
    #test post request
    test_case = base_password_reset
    response = password_reset_post(test_client, test_token, test_case)
    assert b"Your password has been reset." in response.data
    assert test_user.check_password(test_case['password_new']) == True
