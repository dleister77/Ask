from app.models import Category, Provider, Review, User, State
from datetime import date
from flask import url_for, json
import os
from pathlib import Path
from shutil import rmtree
from .test_auth import login, logout


def add_review(client, form, test_app):
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

def provider_profile(client, args, page):
    """Test provider profile route."""
    return client.get(url_for('main.provider', name=args['name'],
                      id=args['id'], _external=False),
                      query_string={"page": page}, follow_redirects=True)

def provider_add(client, form):
    """Add new provider to db."""
    return client.post(url_for('main.providerAdd', _external=False),
                                data=form, follow_redirects=True)    
def providerList(client, form):
    """Test generation of provider lists based on category"""
    return client.post(url_for('main.providerList', _external=False),
                                data=form)
def search(client, form):
    """Test provider search route, returning search results."""
    return client.get(url_for('main.search', _external=False), query_string=form,
                      follow_redirects=True)

def user_profile(client, username, page=None):
    """Get user profile based on username"""
    return client.get(url_for('main.user', username=username, _external=False), 
                      follow_redirects=True, query_string=page)


def test_user(test_client, test_db):
    # test existing user
    login(test_client, "jjones", "password")
    response = user_profile(test_client, "jjones")
    print(response.data.decode())
    assert response.status_code == 200
    name = '<dd class="col-8 text-right">John Jones</dd>'
    assert name in response.data.decode()
    address = '<li class="list-group-item border-0 card-item py-1 px-0">Charlotte, NC, 28210</li>'
    assert address in response.data.decode()
    num_reviews = '<dt class="col-4 text-left"># Reviews:</dt>'
    num_reviews2 = '<dd class="col-8 text-right">2</dd>'
    assert num_reviews in response.data.decode()
    assert num_reviews2 in response.data.decode()
    avg_reviews = '<dd class="col-8 text-right">3.0</dd>'
    assert avg_reviews in response.data.decode()
    pag_link1 = '<li class="page-item"><a class="page-link" href="/user/jjones?page=1">1</a></li>'
    pag_link2 = '<li class="page-item"><a class="page-link" href="/user/jjones?page=2">Next</a></li>'
    assert pag_link1 in response.data.decode()
    assert pag_link2 in response.data.decode()
    pwordmodal = '<form id = "modal_form_group" action="/passwordupdate" method="POST">'
    userupdatemodal = '<form id = "modal_form_group" action="/userupdate" method="POST">'
    assert pwordmodal in response.data.decode()
    assert userupdatemodal in response.data.decode()
    # test page2 of pagination
    page = {"page": 2}
    response = user_profile(test_client, 'jjones', page)
    assert b'Preferred Electric Co' in response.data
    # test user different than logged in
    response = user_profile(test_client, "sarahsmith")
    assert pwordmodal not in response.data.decode()
    assert userupdatemodal not in response.data.decode()
    assert '<dd class="col-8 text-right">sarahsmith@yahoo.com</dd>' in response.data.decode()
    address = '<li class="list-group-item border-0 card-item py-1 px-0">Lakewood, NY, 14750</li>'
    assert address in response.data.decode()
    # test user not related to via group or friendship
    response = user_profile(test_client, 'nukepower4ever')
    assert '<dd class="col-8 text-right">hyman@navy.mil</dd>' not in response.data.decode()

    

def test_review(active_client, test_db, test_app):
    #add review with required information
    user = User.query.filter_by(username="jjones").first()
    test_case = {"category": "1", "name": "2", "rating": "3",
                 "description": "", "service_date": "", "comments": "", 
                 "picture": ""}
    response = add_review(active_client, test_case, test_app)
    assert response.status_code == 200
    assert b'review added' in response.data
    # confirm correct information in db
    filter = {"friends_only": False, "groups_only": False}
    p = Provider.query.filter_by(name="Evers Electric").first()
    assert p.profile(filter)[1] == 3
    assert p.profile(filter)[2] == 1
    # test case without required information
    test_case = {"category": "", "name": "", "rating": "",
                 "description": "outlet install", "service_date": "4/15/2019",
                 "comments": "excellent work", "picture": ""}
    response = add_review(active_client, test_case, test_app)
    assert b"Rating is required" in response.data
    assert response.status_code == 422
    # test case with all fields
    test_case = {"category": "1", "name": "2", "rating": "5",
                 "description": "outlet install", "service_date": "4/15/2019",
                 "comments": "excellent work","picture": ["test.jpg", "eggs.jpg"]}
    response = add_review(active_client, test_case, test_app)
    assert b'review added' in response.data
    assert response.status_code == 200
    path = Path(os.path.join(test_app.config['MEDIA_FOLDER'], str(user.id), 'test.jpg'))
    path2 = Path(os.path.join(test_app.config['MEDIA_FOLDER'], str(user.id), 'eggs.jpg'))
    assert path.is_file()
    assert path2.is_file()
    review = Review.query.filter_by(provider_id=2).all()[1]
    assert review.service_date == date(2019, 4, 15)
    assert review.description == 'Outlet install'
    assert review.comments == 'Excellent work'
    path = os.path.join(test_app.config['MEDIA_FOLDER'], str(user.id))
    rmtree(path)
    #test get request
    response = active_client.get(url_for('main.review', _external=False),
                                 follow_redirects=True)
    assert response.status_code == 200
    assert b"Form disabled. Please verify email to unlock." in response.data
    var = 'disabled="disabled"'
    assert response.data.decode().count(var) == 7


def test_search(active_client, test_db):
    id = State.query.filter_by(name="North Carolina").first().id
    test_case = {"category": 1, "city": "Charlotte", "state": id}
    response = search(active_client, test_case)
    assert response.status_code == 200
    assert b"Douthit Electrical" in response.data
    print(response.data.decode())
    assert '<h4><a href="/provider/Douthit%20Electrical/1">Douthit Electrical</a></h4>' in response.data.decode()
    # test correct stars rendered
    var = '<i class="fas fa-star star-full"></i>'
    assert response.data.decode().count(var) == 3
    # test average rating
    assert '<li class="list-inline-item">3.0</li>' in response.data.decode()
    # test num reviews
    assert '<li class="list-inline-item">(3)</li>' in response.data.decode()
    #test pagination links
    assert '<li class="page-item"><a class="page-link" href="/search?page=2&amp;category=1&amp;city=Charlotte&amp;state=1">Next</a></li>' in response.data.decode()
    test_case = {"category": 1, "city": "Charlotte", "state": id, "page": 2}
    response = search(active_client, test_case)
    assert response.status_code == 200
    assert b'Preferred Electric Co' in response.data
    # test without all required information submitted
    test_case = {"category": 1, "state": id}
    response = search(active_client, test_case)
    assert b"Douthit Electrical" not in response.data
    assert b"City is required" in response.data
    assert response.status_code == 422
    # test friends only
    test_case = {"category": 1, "city": "Charlotte", "state": id, "friends_only":True}
    response = search(active_client, test_case)
    assert b"Douthit Electrical" in response.data
    assert '<li class="list-inline-item">(1)</li>' in response.data.decode()
    assert '<li class="list-inline-item">1.0</li>' in response.data.decode()
    assert '<h4><a href="/provider/Douthit%20Electrical/1?friends_only=y">Douthit Electrical</a></h4>' in response.data.decode()
    # test groups only
    test_case = {"category": 1, "city": "Charlotte", "state": id, "groups_only":True}
    response = search(active_client, test_case)
    assert '<h4><a href="/provider/Douthit%20Electrical/1?groups_only=y">Douthit Electrical</a></h4>' in response.data.decode()
    assert b"Douthit Electrical" in response.data
    assert '<li class="list-inline-item">(1)</li>' in response.data.decode()
    assert '<li class="list-inline-item">5.0</li>' in response.data.decode()


def test_providerList(active_client, test_db):
    test_case = {"category": 1}
    response = providerList(active_client, test_case)
    assert response.status_code == 200
    assert {"id": 1,"name": "Douthit Electrical"} in json.loads(response.data.decode())
    assert {"id": 2,"name": "Evers Electric"} in json.loads(response.data.decode())
    assert {"id": 3,"name": "Preferred Electric Co"} in json.loads(response.data.decode())


def test_providerAdd(active_client, test_db):
    # test provider with multiple categories
    test_case = {"name": "Jims Electric", "category": [1, 2],
                 "address-line1": "2318 Arty Ave", "address-city": "Charlotte",
                 "address-zip": "28208", "address-state": 1,
                 "telephone": "7043346449", "email": "jim@jimselectric.com"}
    response = provider_add(active_client, test_case)
    assert response.status_code == 200
    assert b'Jims Electric added' in response.data
    p = Provider.query.filter_by(name="Jims Electric").first()
    c = Category.query.filter_by(id=1).first()
    c2 = Category.query.filter_by(id=2).first()
    assert c in p.categories
    assert c2 in p.categories
    # test provider with invalid email
    test_case = {"name": "Bobs Electric", "category": [1, 2],
                 "address-line1": "2318 Arty Ave", "address-city": "Charlotte",
                 "address-zip": "28208", "address-state": 1,
                 "telephone": "7043346448", "email": "bobbobselectric.com"}
    response = provider_add(active_client, test_case)
    assert response.status_code == 422
    assert b'Failed to add provider' in response.data
    assert b'Invalid email address' in response.data
    # test provider on GET request
    response = active_client.get(url_for('main.providerAdd', _external=False),
                      follow_redirects=True)
    assert response.status_code == 200
    assert b'id="provideraddform"' in response.data
    assert b"Form disabled. Please verify email to unlock." in response.data
    var = 'disabled="disabled"'
    assert response.data.decode().count(var) == 10


def test_provider_profile(active_client, test_db):
    test_case = {"name": "Douthit Electrical", "id": 1}
    response = provider_profile(active_client, test_case, 1)
    assert b'Reviewer' in response.data
    assert b'Category: Electrician' in response.data
    assert b'Relationship: Self' in response.data
    assert b'<li class="page-item"><a class="page-link" href="/provider/Douthit%20Electrical/1?page=2">2</a></li>' in response.data
    response = provider_profile(active_client, test_case, 2)
    assert b'Friends:  Yes' in response.data
    response = provider_profile(active_client, test_case, 3)
    assert b'Common Groups:' in response.data
    assert b'Qhiv Hoa' in response.data
    test_case = test_case = {"name": "Douthit Electrical", "id": 35}
    response = provider_profile(active_client, test_case, 1)
    assert response.status_code == 404
    

