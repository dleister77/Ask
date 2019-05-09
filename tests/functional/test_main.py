from app.models import Provider, Review, User, State
from datetime import date
from tests.conftest import TestConfig
from flask import url_for, escape
from flask_login import current_user
import io
import os
from pathlib import Path
import pytest
from shutil import rmtree
from .test_auth import login, logout

def user_profile(client, username, page=None):
    """Get user profile based on username"""
    return client.get(url_for('main.user', username=username, _external=False), 
                      follow_redirects=True, query_string=page)

def add_review(client, form):
    """Add review and return response."""
    return client.post(url_for('main.review', _external=False), data=form,
                       follow_redirects=True, buffered=True, content_type='multipart/form-data')

def search(client, form):
    """Test provider search route, returning search results."""
    print(form)
    return client.get(url_for('main.search', _external=False), query_string=form,
                      follow_redirects=True)
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
    

def test_review(test_client, test_db, test_app):
    #add review with required information
    login(test_client, "jjones", "password")
    user = User.query.filter_by(username="jjones").first()
    test_case = {"category": "1", "name": "2", "rating": "3",
                 "description": "", "service_date": "", "comments": "",
                 "picture": ""}
    
    # test_case["picture"] = (io.BytesIO(b"abcdef"), 'test.jpg')
    response = add_review(test_client, test_case)
    assert response.status_code == 200
    assert b'review added' in response.data
    # confirm correct information in db
    p = Provider.query.filter_by(name="Evers Electric").first()
    assert p.profile()[1] == 3
    assert p.profile()[2] == 1
    # test case without required information
    test_case = {"category": "", "name": "", "rating": "",
                 "description": "outlet install", "service_date": "4/15/2019",
                 "comments": "excellent work","picture": ""}
    response = add_review(test_client, test_case)
    assert b"This field is required" in response.data
    # test case with all fields
    test_case = {"category": "1", "name": "2", "rating": "5",
                 "description": "outlet install", "service_date": "4/15/2019",
                 "comments": "excellent work","picture": ""}
    path = os.path.join(test_app.config['MEDIA_FOLDER'], 'source', 'test.jpg')
    with open(path, 'rb') as f:
        test_case['picture'] = (f, f.name)
        response = add_review(test_client, test_case)
    #add multiple file upload
    assert response.status_code == 200
    path = Path(os.path.join(test_app.config['MEDIA_FOLDER'], str(user.id), 'test.jpg'))
    assert path.is_file()
    review = Review.query.filter_by(provider_id=2).all()[1]
    assert review.service_date == date(2019, 4, 15)
    assert review.description == 'Outlet install'
    assert review.comments == 'Excellent work'
    path = os.path.join(test_app.config['MEDIA_FOLDER'], str(user.id))
    rmtree(path)

def test_search(test_client, test_db):
    login(test_client, "jjones", "password")
    id = State.query.filter_by(name="North Carolina").first().id
    test_case = {"category": 1, "city": "Charlotte", "state": id}
    response = search(test_client, test_case)
    assert response.status_code == 200
    print(response.data.decode())
    assert b"Douthit Electrical" in response.data
    assert '<h4><a href="/provider/Douthit-Electrical/1">Douthit Electrical</a></h4>' in response.data.decode()
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
    response = search(test_client, test_case)
    assert b'Preferred Electric Co' in response.data
    # test without all required information submitted
    test_case = {"category": 1, "state": id}
    response = search(test_client, test_case)
    assert b"Douthit Electrical" not in response.data
    assert b"This field is required" in response.data
    # test friends only
    test_case = {"category": 1, "city": "Charlotte", "state": id, "friends_only":True}
    response = search(test_client, test_case)
    assert b"Douthit Electrical" in response.data
    assert '<li class="list-inline-item">(1)</li>' in response.data.decode()
    assert '<li class="list-inline-item">1.0</li>' in response.data.decode()
    # test groups only
    test_case = {"category": 1, "city": "Charlotte", "state": id, "groups_only":True}
    response = search(test_client, test_case)
    assert b"Douthit Electrical" in response.data
    assert '<li class="list-inline-item">(1)</li>' in response.data.decode()
    assert '<li class="list-inline-item">5.0</li>' in response.data.decode()

