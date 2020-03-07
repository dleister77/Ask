from flask import escape, session, url_for
from flask_login import current_user
import pytest

from app.models import State, User
from tests.conftest import login, logout, FunctionalTest


class TestLogin(FunctionalTest):

    routeFunction = 'auth.login'

    def test_new(self, testClient):
        self.form = {"username": "jjones", 'password': 'password'}
        response = self.postRequest(testClient)
        assert response.status_code == 200
        assert b'Search for Business' in response.data
        response = logout(testClient)
        check = testClient.get(url_for('auth.welcome', _external=False),
                                follow_redirects=True)
        assert response.data == check.data
        assert b'Search for Business' not in response.data
    
    def test_loginRequiredPage(self, testClient):
        response = testClient.get(url_for('main.review', _external=False), follow_redirects=True)
        assert b'Please log in to access the requested page' in response.data
    

    def test_invalidPassword(self, testClient):
        self.form = {"username": "jjones", 'password': 'password1234'}        
        response = self.postRequest(testClient)
        assert b'Invalid username or password' in response.data
    
    def test_invalidUsername(self, testClient):
        # test invalid username
        self.form = {"username": "jjones1000", 'password': 'password'} 
        response = self.postRequest(testClient)
        assert b'Invalid username or password' in response.data
    
    def test_alreadyLoggedIn(self, activeClient):
        self.form = {"username": "jjones", 'password': 'password'}
        check = activeClient.get(url_for('main.index', _external=False))
        assert b'Search for Business' in check.data


    def test_alreadyLoggedIn2(self, testClient, testUser2):
        self.form = {"username": "jjones", 'password': 'badpassword'}
        with testClient:
            login(testClient, "sarahsmith",'password1234'
              )
            assert current_user == testUser2
            response = testClient.get(url_for('main.index', _external=False), follow_redirects=True)
            assert b'Search for Business' in response.data
            logout(testClient)

class TestRegister(FunctionalTest):
    
    routeFunction = 'auth.register'

    def test_new(self, testClient, baseUserNew):
        # register new user
        self.form = baseUserNew
        with testClient:
            response = self.postRequest(testClient)
            assert response.status_code == 200
            flash1 = escape("Congratulations! You've successfully registered")
            flash2 = escape('Please check your email for an email verification message.')
            assert flash1.encode() in response.data
            assert flash2.encode() in response.data
            emailVerificationSent = session.get('email_verification_sent')
            assert emailVerificationSent is True
            response = login(testClient, username=baseUserNew['username'],
                            password=baseUserNew['password'])
            assert response.status_code == 200
            assert b'Search for Business' in response.data

    def test_formNotValid(self, testClient, baseUserNew):
        baseUserNew['username'] = 'yardsmith'
        self.form = baseUserNew
        response = self.postRequest(testClient)
        assert b'Username is already registered' in response.data
        assert response.status_code == 422
    
    def test_alreadyLoggedIn(self, activeClient, baseUserNew):
        self.form =baseUserNew
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = escape("You are already registered.")
        assert bytes(flash, 'ascii') in response.data
        assert b'Search for Business' in response.data

class TestUserUpdate(FunctionalTest):

    routeFunction = 'auth.userupdate'

    def test_valid(self, activeClient, baseUser):
        baseUser.update({"last_name": "Johnson", "address-zip": "28212"})
        self.form =baseUser
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        assert b'John Johnson' in response.data
        assert b'28212' in response.data
        assert b'User information updated' in response.data

    def test_invalid(self, activeClient, baseUser):
        # change to email address already in use
        baseUser.update({"email": "sarahsmith@yahoo.com"})
        self.form =baseUser
        response = self.postRequest(activeClient)
        assert b'Email address is already registered' in response.data
        flash = b'User information update failed.  Please correct errors.'
        assert flash in response.data
        assert response.status_code == 422


class TestPasswordUpdate(FunctionalTest):

    routeFunction = 'auth.passwordupdate'

    def test_new(self, activeClient):
        # change password and log back in
        self.form ={"old": "password", "new": "password1", "confirmation": "password1"}
        response = self.postRequest(activeClient)
        assert b'Password updated' in response.data

    def test_invalid(self, activeClient):
        self.form ={"old": "invalidpassword", "new": "password2", "confirmation": "password2"}
        response = self.postRequest(activeClient)
        assert b'Invalid password' in response.data
        assert b'Password update failed' in response.data
        modalOpen = '$("#modal_password").modal("show")'
        assert modalOpen in response.data.decode()


class TestEmailVerify(FunctionalTest):

    routeFunction = 'auth.email_verify'

    def test_new(self, testClient, testUser):
        """Test route for verifying email reset_token."""
        test_token = testUser._get_email_verification_token()
        response = self.getRequest(testClient, token=test_token)
        assert b'Email successfully verified' in response.data
        assert response.status_code == 200
    
    def test_invalid(self, testClient, testUser):
        test_token = testUser._get_email_verification_token(expiration=-200)
        response = self.getRequest(testClient, token=test_token)
        assert b"Email verification failed due to expiration of verification code"\
            in response.data 



class TestEmailVerificationRequest(FunctionalTest):

    routeFunction = 'auth.email_verify_request'

    def test_notAuthenticated(self, testClient):
        """Test route for email reset to be sent."""
        response = self.getRequest(testClient)
        assert b'Please log in to request a new email verification link.' in response.data
        
    def test_authenticated(self, activeClient, baseUser):
        response = self.getRequest(activeClient)
        assert b'Please check your email for an email verification message.' in response.data
        assert session['email_verification_sent'] is True

class TestPasswordResetRequest(FunctionalTest):

    routeFunction = 'auth.password_reset_request'


    def test_get(self, testClient, baseUser):
        """Test route request password reset email to be sent."""
        response = self.getRequest(testClient)
        assert response.status_code == 200
        assert "<h3>Password Reset Request</h3>" in response.data.decode()
        
    def test_post(self, testClient, baseUser):
        self.form ={"email": baseUser["email"]}
        response = self.postRequest(testClient)
        assert b"Check email for instructions to reset your password" in response.data
        assert response.status_code == 200

class TestPasswordReset(FunctionalTest):
    
    routeFunction = 'auth.passwordreset'
    

    def test_get(self, testClient, testUser):
        """Test actual resetting of password via password reset request."""
        test_token = testUser._get_reset_password_token()    
        # test get request
        response = self.getRequest(testClient, token=test_token)
        assert response.status_code == 200
        assert "<h3>Password Reset</h3>" in response.data.decode()

    def test_post(self, testClient, testUser, basePasswordReset):
        #test post request
        self.client = testClient
        test_token = testUser._get_reset_password_token()  
        self.form =basePasswordReset
        response = self.postRequest(testClient, token=test_token)
        print(current_user)
        assert b"Your password has been reset." in response.data
        assert testUser.check_password(self.form['password_new']) is True
    
    def test_postInvalid(self, testClient, testUser, basePasswordReset):
        self.client = testClient
        test_token = testUser._get_reset_password_token()
        basePasswordReset['password_new'] = 'password4'
        self.form =basePasswordReset
        response = self.postRequest(testClient, token=test_token)
        assert "<h3>Password Reset</h3>" in response.data.decode()
        flash = b"Password reset failed.  Please correct errors."
        assert flash in response.data
