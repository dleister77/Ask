from datetime import date
import json
import os
from pathlib import Path
from shutil import rmtree

from flask import url_for, current_app
from flask_login import current_user

from app.models import Category, Provider, Review, Provider_Suggestion,\
    Address_Suggestion, Picture
from tests.conftest import FunctionalTest


def addPicsToForm(client, form, app):
    """Add review and return response."""
    #only do below if files exists
    if 'picture' in form and form['picture'] != "":
    # list of files to upload
        files = form['picture'][:]
        form['picture'] = []
        # open each file, append data and name to list
        try:
            for file in files:
                f = open(os.path.join(app.config['MEDIA_FOLDER'], 'source', file), 'rb')
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
    edituserinfo = '<i class="material-icons">edit</i>'
    changepassword = '<a href="" data-toggle="modal" data-target="#modal_password">Click to update password</a>'

    def test_get(self, activeClient, testUser):
        # test existing user
        response = self.getRequest(activeClient, username=testUser.username)
        responseDecoded = response.data.decode()
        print(responseDecoded)
        assert response.status_code == 200
        name = '<dd class="col-8 text-right">John Jones</dd>'
        assert name in responseDecoded
        address = '<li class="list-group-item border-0 card-item py-1 px-0">Charlotte, NC, 28210</li>'
        assert address in responseDecoded
        num_reviews = '<dt class="col-4 text-left"># Reviews:</dt>'
        num_reviews2 = '<dd class="col-8 text-right">3</dd>'
        assert num_reviews in responseDecoded
        assert num_reviews2 in responseDecoded
        avg_reviews = f'<dd class="col-8 text-right">4.0</dd>'
        assert avg_reviews in responseDecoded
        pag_link1 = '<li class="page-item"><a class="page-link" href="/user/jjones?page=1">1</a></li>'
        pag_link2 = '<li class="page-item"><a class="page-link" href="/user/jjones?page=2">Next</a></li>'
        assert pag_link1 in responseDecoded
        assert pag_link2 in responseDecoded
        assert self.pwordmodal in responseDecoded
        assert self.edituserinfo in responseDecoded
        assert self.userupdatemodal in responseDecoded
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

    def postRequest(self, client, app=None, **kwargs):
        """Add review and return response."""
        #only do below if files exists
        if 'picture' in self.form and self.form['picture'] != "":
        # list of files to upload
            files = self.form['picture'][:]
            self.form['picture'] = []
            try:
                for file in files:
                    path = os.path.join(app.config['MEDIA_FOLDER'], 'source', file)
                    f = open(path, 'rb')
                    self.form['picture'].append((f, file))
                return client.post(url_for(self.routeFunction, **kwargs, _external=False), data=self.form,
                follow_redirects=True, buffered=True, content_type='multipart/form-data')
            finally:
                for file in self.form['picture']:
                    file[0].close()                
        else:
            return super().postRequest(client, **kwargs)

    def test_postNew(self, activeClient, testUser, baseReview):
        # add review with required information
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

    def test_postWithPicture(self, activeClient, testUser, baseReview, app):
        baseReview.update({"picture": ["test.jpg", "nyc.jpg"]})
        self.form = baseReview
        response = self.postRequest(activeClient, app)
        try:
            assert b'review added' in response.data
            assert response.status_code == 200
            path1 = Path(
                os.path.join(
                    app.config['MEDIA_FOLDER'], str(testUser.id),
                    f'{testUser.username}_1.jpg'
                )
            )
            path2 = Path(
                os.path.join(
                    app.config['MEDIA_FOLDER'], str(testUser.id),
                    f'{testUser.username}_2.jpg'
                )
            )
            assert path1.is_file()
            assert path2.is_file()
            picture1 = Picture.query.filter_by(path=str(path1)).first()
            assert picture1 is not None
            picture2 = Picture.query.filter_by(path=str(path2)).first()
            assert picture2 is not None
            review = Review.query.filter_by(provider_id=baseReview['id']).all()
            review = review[0]
            assert review.service_date == date(2019, 4, 15)
            assert review.description == baseReview['description']
            assert review.comments == baseReview['comments']
        finally:
            path = os.path.join(app.config['MEDIA_FOLDER'], str(testUser.id))
            rmtree(path)

    def test_getEmailVerified(self, activeClient, testUser, testProvider1):
        testUser.update(email_verified=True)
        assert testUser.email_verified is True
        response = self.getRequest(activeClient, name=testProvider1.name,
                                   id=testProvider1.id)
        assert response.status_code == 200
        newPageHeader = b'<h3>Add Review</h3>'
        assert newPageHeader in response.data
        var2 = 'readonly'
        assert response.data.decode().count(var2) == 2
    
    def test_getEmailNotVerified(self, activeClient, testUser, testProvider1):
        assert testUser.email_verified is False
        response = self.getRequest(activeClient, name=testProvider1.name,
                                   id=testProvider1.id)
        assert response.status_code == 200
        newPageHeader = b'<h3>Add Review</h3>'
        assert newPageHeader in response.data
        assert b"Form disabled. Please verify email to unlock." in response.data
        var = 'disabled'
        assert response.data.decode().count(var) == 21
        var2 = 'readonly'
        assert response.data.decode().count(var2) == 2

  
    def test_getNoArgs(self, activeClient):
        response = self.getRequest(activeClient)
        flash = b'Invalid request. Please search for provider first and then add review.'
        assert flash in response.data
        newPageHeader = b'<h3>Search for Business</h3>'
        assert newPageHeader in response.data

class TestReviewEdit(FunctionalTest):

    routeFunction = 'main.reviewEdit'

    def cleanup(self):
        path = Path(
            os.path.join(
                current_app.config['MEDIA_FOLDER'],
                str(current_user.id)
            )
        )
        try:
            rmtree(path)
        except FileNotFoundError:
            raise

    def postRequest(self, client, app=None, **kwargs):
        """Add review and return response."""
        #only do below if files exists
        if 'picture' in self.form and self.form['picture'] != "":
        # list of files to upload
            files = self.form['picture'][:]
            self.form['picture'] = []
            try:
                for file in files:
                    path = os.path.join(app.config['MEDIA_FOLDER'], 'source', file)
                    f = open(path, 'rb')
                    self.form['picture'].append((f, file))
                return client.post(url_for(self.routeFunction, **kwargs, _external=False), data=self.form,
                follow_redirects=True, buffered=True, 
                content_type='multipart/form-data')
            finally:
                for file in self.form['picture']:
                    file[0].close()                
        else:
            return super().postRequest(client, **kwargs)    

    def test_get(self, activeClient, testReview, testPicture):
        current_user.email_verified = True
        referrer = url_for('main.user', username=current_user.username)
        headers = dict(referer=referrer)
        response = self.getRequest(activeClient, id=testReview.id,headers=headers)
        assert response.status_code == 200
        var = 'readonly'
        assert response.data.decode().count(var) == 2
        assert testReview.provider.name.encode() in response.data
        url = url_for('main.download_file', id=current_user.id, filename=testReview.pictures[0].name)
        img = f'<img src="{url}" alt="" class="thumbnail">'  
        assert img.encode() in response.data
    
    def test_PostValidDeletePicture(self, activeClient, baseReviewEdit, app, testPicture):
        current_user.email_verified = True
        assert testPicture.is_file()
        picture_name = testPicture.name
        id = Picture.query.filter_by(name=picture_name).first().id
        baseReviewEdit['deletePictures'] = [id]
        self.form = baseReviewEdit
        response = self.postRequest(activeClient, app=app, id=self.form['id'])
        assert response.status_code == 200
        assert not testPicture.is_file()
        self.cleanup()

    def test_PostValidAddPicture(self, activeClient, baseReviewEdit, app):
        current_user.email_verified = True
        baseReviewEdit.update({"picture": ["nyc.jpg"]})
        self.form = baseReviewEdit
        response = self.postRequest(activeClient, app=app, id=self.form['id'])
        assert response.status_code == 200
        new_picture_path = Path(
            os.path.join(
                current_app.config['MEDIA_FOLDER'], str(current_user.id),
                f'{current_user.username}_1.jpg'
            )
        )
        assert new_picture_path.is_file()
        review = Review.query.get(self.form.get('id'))
        assert review is not None
        assert len(review.pictures) == 2
        self.cleanup()


    def test_PostValidAddDeletePicture(self, activeClient, testPicture, baseReviewEdit, app):
        current_user.email_verified = True
        baseReviewEdit.update({"picture": ["nyc.jpg"]})
        picture_name = testPicture.name
        id = Picture.query.filter_by(name=picture_name).first().id
        baseReviewEdit['deletePictures'] = [id]
        self.form = baseReviewEdit
        response = self.postRequest(activeClient, app=app, id=self.form['id'])
        assert response.status_code == 200
        new_picture_path = Path(
            os.path.join(
                current_app.config['MEDIA_FOLDER'], str(current_user.id),
                f'{current_user.username}_1.jpg'
            )
        )
        assert new_picture_path.is_file()
        review = Review.query.get(self.form.get('id'))
        assert review is not None
        assert len(review.pictures) == 2
        num_pics = len(os.listdir(new_picture_path.parent))
        assert num_pics == 1
        self.cleanup()

    def test_postInvalid(self, activeClient, baseReviewEdit, app, testPicture):
        current_user.email_verified = True
        baseReviewEdit.pop('rating')
        self.form = baseReviewEdit
        response = self.postRequest(
            activeClient, app=app, id=self.form.get('id')
        )
        assert response.status_code == 422
        flash = 'Please correct form errors.'
        assert flash.encode() in response.data
        error = "Rating is required."
        assert error.encode() in response.data

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

    def test_search(self, activeClient, baseProviderSearch, testProvider1):
        test_case = baseProviderSearch
        response = self.getRequest(activeClient, **test_case)
        assert response.status_code == 200
        pageHeader = b'<h3>Search for Business</h3>'
        assert pageHeader in response.data
        resultsDiv = b'<div id="list_items"'
        assert resultsDiv in response.data
        autocompleteURL = b'/provider/list/autocomplete'
        assert autocompleteURL in response.data
        provider1Url = f"http://{testProvider1.website}"
        assert provider1Url.encode() in response.data
        providerCard = b'<div class="card">'
        assert response.data.count(providerCard) == 2
        #TODO: fix test for proper json rendering on search page script block
        # searchHome = '\"address\": \"\", \"coordinates\": [35.123947, -80.864784], \"latitude\": 35.123947, \"longitude\": -80.864784, \"source\": \"home\"}'
        # assert searchHome in response.data.decode()
        full = b'<i class="fas fa-star card-star"></i>'
        assert response.data.count(full) == 2
        half = b'<i class="fas fa-star-half-alt card-star"></i>'
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
        check = {"id": 1, "name": "Douthit Electrical", "line1": "6000 Fairview Rd",\
                "city": "Charlotte", "state": "NC"}
        output = json.loads(response.data.decode())
        assert check in output


    def test_searchMultiple(self, activeClient, baseProviderSearch):
            baseProviderSearch.update({"name":"er"})
            test_case = baseProviderSearch
            response = self.getRequest(activeClient, **test_case)
            assert response.status_code == 200
            check1 = {"id": 2, "name": "Evers Electric", "line1": "3924 Cassidy Drive",\
                    "city": "Waxhaw", "state": "NC"}
            check2 = {"id": 3, "name": "Preferred Electric Co", "line1": "4113 Yancey Rd",\
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
        var = 'disabled id'
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
        print(response.data.decode())
        assert b'QHIV HOA' in response.data
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


class TestProviderSuggestion(FunctionalTest):

    routeFunction = "main.make_provider_suggestion"

    def test_success(self, activeClient):
        num_suggestions = len(Provider_Suggestion.query.all())
        assert num_suggestions == 0
        self.form = dict(
            id=1,
            name="Douthit Electrical",
            is_not_active=True,
            category_updated=True,
            sector="1",
            category="2",
            contact_info_updated="true",
            email="doug@test.com",
            website="www.test.com",
            telephone="1234567890",
            address_updated=True,
            line1="7708 Covey Chase Dr",
            line2="",
            city="charlotte",
            state="1",
            zip="28210",
            is_coordinate_error=False,
        )
        response = self.postRequest(activeClient)
        assert response.status_code == 200, f'Incorrect Status Code: expected 200, received {response.status_code}, {json.loads(response.data.decode())}'
        num_suggestions = len(Provider_Suggestion.query.all())
        assert num_suggestions == 1
        num_addr_suggestion = len(Address_Suggestion.query.all())
        assert num_addr_suggestion == 1


    def test_success_no_address(self, activeClient):
        num_suggestions = len(Provider_Suggestion.query.all())
        assert num_suggestions == 0        
        self.form = dict(
            id=1,
            name="Douthit Electrical",
            is_not_active="false",
            category_updated="true",
            sector="1",
            category="2",
            contact_info_updated="true",
            email="doug@test.com",
            website="www.test.com",
            telephone="1234567890",
            address_updated="false",
        )
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        num_suggestions = len(Provider_Suggestion.query.all())
        assert num_suggestions == 1

    def test_failed_missing_address(self, activeClient):
        num_suggestions = len(Provider_Suggestion.query.all())
        assert num_suggestions == 0        
        self.form = dict(
            id=1,
            name="Douthit Electrical",
            category_updated="true",
            sector="1",
            category="2",
            contact_info_updated="true",
            email="doug@test.com",
            website="www.test.com",
            telephone="1234567890",
            address_updated="true",

        )
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        num_suggestions = len(Provider_Suggestion.query.all())
        assert num_suggestions == 0