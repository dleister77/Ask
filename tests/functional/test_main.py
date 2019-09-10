from datetime import date
import os
from pathlib import Path
import re
from shutil import rmtree

from flask import url_for, json
from flask_login import current_user

from app.models import Category, Provider, Review, User, State
from .test_auth import login, logout
from tests.conftest import FunctionalTest


def addPicsToForm(client, form, test_app):
    """Add review and return response."""
    #only do below if files exists
    if 'picture' in form and form['picture'] != "":
    # list of files to upload
        files = form['picture'][:]
        form['picture'] = []
        # open each file, append data and name to list
        try:
            for file in files:
                f = open(os.path.join(test_app.config['MEDIA_FOLDER'], 'source', file), 'rb')
                form['picture'].append((f, f.name))
            return client.post(url_for('main.review', _external=False), data=form,
            follow_redirects=True, buffered=True, content_type='multipart/form-data')
        finally:
            #once response generate, close each file
            for file in form['picture']:
                file[0].close()

    return client.post(url_for('main.review', _external=False), data=form,
                       follow_redirects=True, buffered=True, content_type='multipart/form-data')

class TestUser(FunctionalTest):

    routeFunction = 'main.user'
    pwordmodal = '<form id = "modal_form_group" action="/passwordupdate" method="POST">'
    userupdatemodal = '<form id = "modal_form_group" action="/userupdate" method="POST">'
    edituserinfo = '<a href="" data-toggle="modal" data-target="#modal_id">(edit)</a>'
    changepassword = '<a href="" data-toggle="modal" data-target="#modal_password">Click to update password</a>'

    def test_get(self, activeClient, testUser):
        # test existing user
        response = self.getRequest(activeClient, username=testUser.username)
        responseDecoded = response.data.decode()
        assert response.status_code == 200
        name = '<dd class="col-8 text-right">John Jones</dd>'
        assert name in responseDecoded
        address = '<li class="list-group-item border-0 card-item py-1 px-0">Charlotte, NC, 28210</li>'
        assert address in responseDecoded
        num_reviews = '<dt class="col-4 text-left"># Reviews:</dt>'
        num_reviews2 = '<dd class="col-8 text-right">3</dd>'
        assert num_reviews in responseDecoded
        assert num_reviews2 in responseDecoded
        avg_reviews = '<dd class="col-8 text-right">4.0</dd>'
        assert avg_reviews in responseDecoded
        pag_link1 = '<li class="page-item"><a class="page-link" href="/user/jjones?page=1">1</a></li>'
        pag_link2 = '<li class="page-item"><a class="page-link" href="/user/jjones?page=2">Next</a></li>'
        assert pag_link1 in responseDecoded
        assert pag_link2 in responseDecoded
        assert self.pwordmodal in responseDecoded
        assert self.userupdatemodal in responseDecoded
        assert self.edituserinfo in responseDecoded
        assert self.changepassword in responseDecoded

    def test_getPage2(self, activeClient, testUser):
        # test page2 of pagination
        response = self.getRequest(activeClient, username=testUser.username,
                                   page=2)
        assert b'Preferred Electric Co' in response.data
        
    def test_differentUser(self, activeClient, testUser2):
        response = self.getRequest(activeClient, username=testUser2.username)
        responseDecoded = response.data.decode()
        assert self.pwordmodal not in responseDecoded
        assert self.userupdatemodal not in responseDecoded
        assert self.changepassword not in responseDecoded
        assert self.edituserinfo not in responseDecoded
        assert '<dd class="col-8 text-right">sarahsmith@yahoo.com</dd>' in response.data.decode()
        address = '<li class="list-group-item border-0 card-item py-1 px-0">Lakewood, NY, 14750</li>'
        assert address in responseDecoded
    
    def test_userNotRelated(self, activeClient, testUser4):
        response = self.getRequest(activeClient, username=testUser4.username)
        assert '<dd class="col-8 text-right">hyman@navy.mil</dd>' not in response.data.decode()

    
class TestReview(FunctionalTest):

    routeFunction = 'main.review'

    def postRequest(self, client, test_app=None, **kwargs):
        """Add review and return response."""
        #only do below if files exists
        if 'picture' in self.form and self.form['picture'] != "":
        # list of files to upload
            files = self.form['picture'][:]
            self.form['picture'] = []
            try:
                for file in files:
                    path = os.path.join(test_app.config['MEDIA_FOLDER'], 'source', file)
                    f = open(path, 'rb')
                    self.form['picture'].append((f, file))
                return client.post(url_for(self.routeFunction, _external=False), data=self.form,
                follow_redirects=True, buffered=True, content_type='multipart/form-data')
            finally:
                for file in self.form['picture']:
                    file[0].close()                
        else:
            return super().postRequest(client, **kwargs)

    def test_postNew(self, activeClient, testUser, baseReview):
        #add review with required information
        testUser.emailVerified = True
        self.form = baseReview
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        assert b'review added' in response.data
        newPageHeader = b'<h3>Search for Business</h3>'
        assert newPageHeader in response.data
        # confirm correct information in db
        filter = {"friends_filter": False, "groups_filter": False}
        p = Provider.query.filter_by(name="Evers Electric").first()
        assert p.profile(filter)[1] == 3
        assert p.profile(filter)[2] == 3
        assert p.profile(filter)[3] == 1
    
    
    def test_postInvalidForm(self, activeClient, testUser, baseReview):
        # test case without required information
        baseReview.update({"rating": ""})
        self.form = baseReview
        response = self.postRequest(activeClient)
        assert b"Rating is required" in response.data
        newPageHeader = b'<h3>Add Review</h3>'
        assert newPageHeader in response.data
        assert response.status_code == 422

    def test_postWithPicture(self, activeClient, testUser, baseReview, test_app):
        baseReview.update({"picture": ["test.jpg", "nyc.jpg"]})
        self.form = baseReview
        response = self.postRequest(activeClient, test_app)
        try:
            assert b'review added' in response.data
            assert response.status_code == 200
            path = Path(os.path.join(test_app.config['MEDIA_FOLDER'], str(testUser.id), 'test.jpg'))
            path2 = Path(os.path.join(test_app.config['MEDIA_FOLDER'], str(testUser.id), 'nyc.jpg'))
            assert path.is_file()
            assert path2.is_file()
            review = Review.query.filter_by(provider_id=baseReview['id']).all()
            review = review[0]
            assert review.service_date == date(2019, 4, 15)
            assert review.description == baseReview['description'].capitalize()
            assert review.comments == baseReview['comments'].capitalize()
        finally:
            path = os.path.join(test_app.config['MEDIA_FOLDER'], str(testUser.id))
            rmtree(path)

    def test_getEmailVerified(self, activeClient, testUser, testProvider1):
        testUser.update(email_verified=True)
        assert testUser.email_verified is True
        response = self.getRequest(activeClient, name=testProvider1.name,
                                   id=testProvider1.id)
        assert response.status_code == 200
        newPageHeader = b'<h3>Add Review</h3>'
        assert newPageHeader in response.data
        var = 'disabled'
        assert response.data.decode().count(var) == 1 # 1 field and 1 comments
        var2 = 'readonly'
        assert response.data.decode().count(var2) == 1
    
    def test_getEmailNotVerified(self, activeClient, testUser, testProvider1):
        assert testUser.email_verified is False
        response = self.getRequest(activeClient, name=testProvider1.name,
                                   id=testProvider1.id)
        assert response.status_code == 200
        newPageHeader = b'<h3>Add Review</h3>'
        assert newPageHeader in response.data
        assert b"Form disabled. Please verify email to unlock." in response.data
        var = 'disabled'
        print(response.data.decode())

        assert response.data.decode().count(var) == 19
        var2 = 'readonly'
        assert response.data.decode().count(var2) == 1
    
    
    def test_getNoArgs(self, activeClient):
        response = self.getRequest(activeClient)
        flash = b'Invalid request. Please search for provider first and then add review.'
        assert flash in response.data
        newPageHeader = b'<h3>Search for Business</h3>'
        assert newPageHeader in response.data

class TestIndex(FunctionalTest):

    routeFunction = 'main.index'

    def test_get(self, activeClient):
        response = self.getRequest(activeClient)
        assert response.status_code == 200
        pageHeader = b'<h3>Search for Business</h3>'
        assert pageHeader in response.data
        resultsDiv = b'<div id="businessList">'
        assert resultsDiv not in response.data #no results rendered


class TestProviderSearch(FunctionalTest):

    routeFunction = 'main.search'

    def test_search(self, activeClient, baseProviderSearch):
        test_case = baseProviderSearch
        response = self.getRequest(activeClient, **test_case)
        assert response.status_code == 200
        pageHeader = b'<h3>Search for Business</h3>'
        assert pageHeader in response.data
        resultsDiv = b'<div id="businessList">'
        assert resultsDiv in response.data
        autocompleteURL = b'/provider/list/autocomplete'
        assert autocompleteURL in response.data
        providerCard = b'<div class="card">'
        assert response.data.count(providerCard) == 2
        searchHome = b'{"address": "", "coordinates": [35.123949, -80.864783], "latitude": 35.123949, "longitude": -80.864783, "source": "home"}';
        assert searchHome in response.data
        # test correct stars rendered
        full = b'<i class="fas fa-star star-full"></i>'
        assert response.data.count(full) == 2
        half = b'<i class="fas fa-star-half-alt star-half"></i>'
        assert response.data.count(half) == 1
    
    def test_searchNoResults(self, activeClient, baseProviderSearch):
        baseProviderSearch.update({"name": "Test Electrician"})
        test_case = baseProviderSearch
        response = self.getRequest(activeClient, **test_case)
        flash = b'No results found. Please try a different search.'
        assert flash in response.data
        resultsDiv = b'<div id="businessList">'
        assert resultsDiv not in response.data
        autocompleteURL = b'/provider/list/autocomplete'
        assert autocompleteURL in response.data

    def test_badAddress(self, activeClient, baseProviderSearch):
        baseProviderSearch.update({"location": "manual",
        "manual_location": "7000 covey chase dr charlotte nc"
        })
        test_case = baseProviderSearch
        response = self.getRequest(activeClient, **test_case)
        flash = b'Invalid address submitted. Please re-enter and try again.'
        assert flash in response.data
        assert response.status_code == 422

class TestProviderList(FunctionalTest):

    routeFunction = 'main.provider_list'

    def test_providerList(self, activeClient):
        test_case = {"category": 1}
        response = self.getRequest(activeClient, **test_case)
        assert response.status_code == 200
        assert {"id": 1,"name": "Douthit Electrical"} in json.loads(response.data.decode())
        assert {"id": 2,"name": "Evers Electric"} in json.loads(response.data.decode())
        assert {"id": 3,"name": "Preferred Electric Co"} in json.loads(response.data.decode())

class TestProviderAutocomplete(FunctionalTest):

    routeFunction = 'main.providerAutocomplete'

    def test_search(self, activeClient, baseProviderSearch):
        baseProviderSearch.update({"name":"Dou"})
        test_case = baseProviderSearch
        response = self.getRequest(activeClient, **test_case)
        assert response.status_code == 200
        check = {"name": "Douthit Electrical", "line1": "6000 Fairview Rd",\
                "city": "Charlotte", "state": "NC"}
        assert check in json.loads(response.data.decode())


    def test_searchMultiple(self, activeClient, baseProviderSearch):
            baseProviderSearch.update({"name":"er"})
            test_case = baseProviderSearch
            response = self.getRequest(activeClient, **test_case)
            assert response.status_code == 200
            check1 = {"name": "Evers Electric", "line1": "3924 Cassidy Drive",\
                    "city": "Waxhaw", "state": "NC"}
            check2 = {"name": "Preferred Electric Co", "line1": "4113 Yancey Rd",\
                    "city": "Charlotte", "state": "NC"}
            assert check1 in json.loads(response.data.decode())
            assert check2 in json.loads(response.data.decode())

    def test_invalidAddress(self, activeClient, baseProviderSearch):
        baseProviderSearch.update({"name":"Dou", "location": "manual",
        "manual_location": "7000 covey chase dr charlotte nc" })
        test_case = baseProviderSearch
        response = self.getRequest(activeClient, **test_case)
        assert response.status_code == 422
        check = {"status": "failed", "reason": "invalid address"}
        for k,v in check.items():
            assert k,v in response.json.items()
        # 

class TestProviderAdd(FunctionalTest):

    routeFunction = 'main.provider_add'

    def test_success(self, activeClient, baseProviderNew):
        self.form = baseProviderNew
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        assert b'Smith Electric added' in response.data
        p = Provider.query.filter_by(name="Smith Electric").first()
        c = Category.query.filter_by(id=1).first()
        c2 = Category.query.filter_by(id=2).first()
        assert c in p.categories
        assert c2 in p.categories


    def test_invalidFormData(self, activeClient, baseProviderNew):
        baseProviderNew.update({"email": "testtest.com"})
        self.form = baseProviderNew
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        print(response.data.decode())
        assert b'Failed to add provider' in response.data
        assert 'Invalid email address' in response.data.decode()
       
    def test_emailNotVerified(self, activeClient):
        response = self.getRequest(activeClient)
        assert b"Form disabled. Please verify email to unlock." in response.data
        var = 'disabled'
        assert response.data.decode().count(var) == 13

    def test_getRequest(self, activeClient):
        current_user.email_verified = True
        response = self.getRequest(activeClient)
        assert b"Form disabled. Please verify email to unlock." not in response.data
        assert response.status_code == 200
        assert b'id="provideraddform"' in response.data


class TestProviderProfile(FunctionalTest):

    routeFunction = 'main.provider'


    def test_page1(self, activeClient, testProvider1):
        test_case = {"name": testProvider1.name, "id": testProvider1.id}
        response = self.getRequest(activeClient, **test_case)
        assert b'Reviewer' in response.data
        assert b'Category: Electrician, Plumber' in response.data
        assert b'Qhiv Hoa' in response.data
        assert b'Relationship: Self' in response.data
        assert b'<li class="page-item"><a class="page-link" href="/provider/Douthit%20Electrical/1?page=2">2</a></li>' in response.data
        
    def test_page2(self, activeClient, testProvider1):
        test_case = {"name": testProvider1.name, "id": testProvider1.id, "page": 2}
        response = self.getRequest(activeClient, **test_case)
        assert b'Friends:  Yes' in response.data
        assert b'<li class="page-item"><a class="page-link" href="/provider/Douthit%20Electrical/1?page=1">1</a></li>' in response.data

    def test_invalidID(self, activeClient, testProvider1):
        test_case = {"name": "Douthit Electrical", "id": 35}
        response = self.getRequest(activeClient, **test_case)
        assert response.status_code == 404
        flash = b'Provider not found.  Please try a different search.'
        assert flash in response.data

    

