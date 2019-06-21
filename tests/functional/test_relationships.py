from app.helpers import dbUpdate
from app.models import User, Group
from flask import escape, url_for
from flask_login import current_user
import pytest

from tests.conftest import scenarioUpdate, login, logout

def network(client):
    return client.get(url_for('relationship.network', _external=False),
                      follow_redirects=True)

def groupsearch(client, args):
    return client.get(url_for('relationship.groupsearch', _external=False),
                      follow_redirects=True, query_string=args)

def friendadd(client, form):
    return client.post(url_for('relationship.friendadd', _external=False),
                      follow_redirects=True, data=form)

def friendsearch(client, args):
    return client.get(url_for('relationship.friendsearch', _external=False),
                      follow_redirects=True, query_string=args)

def groupadd(client, form):
    return client.post(url_for('relationship.groupadd', _external=False),
                      follow_redirects=True, data=form)

def groupcreate(client, form):
    return client.post(url_for('relationship.groupcreate', _external=False),
                      follow_redirects=True, data=form)

def groupcreate_get(client):
    return client.get(url_for('relationship.groupcreate', _external=False),
                      follow_redirects=True)

def groupUpdate(client, form):
    return client.post(url_for('relationship.groupUpdate', _external=False),
                      follow_redirects=True, data=form)

def groupProfile(client, test_case):
    return client.get(url_for('relationship.group', name=test_case['name'],
                      id=test_case['id'], _external=False),
                      follow_redirects=True)

def test_network(active_client, test_db):
    response = network(active_client)
    assert '<li> <a href="/user/sarahsmith"> Sarah Smith </a></li>' in response.data.decode()
    assert '<li> <a href="/group/Qhiv%20Hoa/1"> Qhiv Hoa </a></li>' in response.data.decode()
    assert b'Mark Johnson' not in response.data
    assert '<form id = "modal_form_group" action="" method="POST">' in response.data.decode()
    assert response.data.decode().count("Qhiv Hoa") == 1
    assert b"Create new group disabled. Please verify email to unlock" in response.data
    var = 'disabled="disabled"'
    assert response.data.decode().count(var) == 3
    User.query.get(2).update(email_verified=True)
    dbUpdate()
    response = network(active_client)
    assert b"Create new group disabled. Please verify email to unlock" not in response.data  

def test_group(test_client, test_db):
    login(test_client, "jjones", "password")
    #base request.  User not group admin
    test_case = {"name": "Qhiv Hoa", "id": "1"}
    response = groupProfile(test_client, test_case)
    print(response.data.decode())
    assert response.status_code == 200
    assert '<a href="" data-toggle="modal" data-target="#modal_id">(edit)</a>' in response.data.decode()
    assert '<a href="/user/yardsmith">' in response.data.decode()
    assert response.data.decode().count('John Jones') == 2

    #test user who is not admin
    logout(test_client)
    login(test_client, "yardsmith", "password5678")
    response = groupProfile(test_client, test_case)
    assert response.status_code == 200
    assert '<a href="" data-toggle="modal" data-target="#modal_id">(edit)</a>' not in response.data.decode()
    assert response.data.decode().count('Mark Johnson') == 1

    #test user who is not group member
    logout(test_client)
    login(test_client, "sarahsmith", "password1234")
    response = groupProfile(test_client, test_case)
    assert '<a href="" data-toggle="modal" data-target="#modal_id">(edit)</a>' not in response.data.decode()
    assert response.data.decode().count('Mark Johnson') == 0    
  


def test_group_update(test_client, test_db, base_group):
    
    login(test_client, "jjones", "password")
    test_case = base_group.copy()
    #invalid input
    test_case['name'] = ""
    response = groupUpdate(test_client, test_case)
    assert response.status_code == 422
    assert b'Group name is required.' in response.data
    
    #test name change
    test_case['name'] = 'Jens Bees'
    test_case['description'] = 'Another description'
    print(test_case)
    response = groupUpdate(test_client, test_case)
    print(response.data.decode())
    g = Group.query.filter_by(id=2).first()
    assert response.status_code == 200
    assert b'Group information updated' in response.data
    assert g.name == 'Jens Bees'

    #test non admin attempting changes
    logout(test_client)
    login(test_client, "sarahsmith", "password1234")
    test_case['name'] = "Dougs bees" 
    response = groupUpdate(test_client, test_case)
    assert response.status_code == 422
    assert b'User not authorized to make changes' in response.data



@pytest.mark.parametrize('name, assertion',
                          [("Shannon's Bees", ["Shannon's Bees"]),
                          ("shannon's bees", ["Shannon's Bees"]),
                          ("sha", ["Shannon's Bees", "Shawshank Redemption Fans"]),
                          ("shannons bees", ["Shannon's Bees"])
                          ])
def test_groupsearch(test_client, test_db, name, assertion):
    login(test_client, "jjones", "password")
    test_case = {"name": name}
    response = groupsearch(test_client, test_case)
    for a in assertion:
        assert bytes(a, encoding='utf-8') in response.data


@pytest.mark.parametrize('name', ['Sarah Smith', 'sarah smith',
                         'smith sarah', 'smith'])
def test_friendsearch(test_client, test_db, name):
    login(test_client, "jjones", "password")
    test_case = {"name": name}
    response = friendsearch(test_client, test_case)
    assert '{"city":"Lakewood","first_name":"Sarah","id":1,"last_name":"Smith","state":"NY"}' in response.data.decode()


@pytest.mark.parametrize('id, name, assertion',
                          [(3, "Mark Johnson", b"You are now friends with Mark Johnson"),
                          (1, "Sarah Smith", b"You are already friends with this person"),
                          (2, "John Jones", b"You are naturally friends with yourself")])
def test_friendadd(test_client, test_db, id, name, assertion):
        login(test_client, "jjones", "password")
        test_case = {"value": id, "name": name}
        response = friendadd(test_client, test_case)
        assert assertion in response.data

@pytest.mark.parametrize('id, name, assertion',
                          [(2, "Shannon's Bees", "You are now a member of Shannon's Bees"),
                          (1, "Qhiv Hoa", "You are already a member of this group"),
                          (4, "Liverpool FC", "Group does not exist, please choose a different group")])
def test_groupadd(test_client, test_db, id, name, assertion):
        login(test_client, "jjones", "password")
        test_case = {"value": id, "name": name}
        response = groupadd(test_client, test_case)
        assertion = bytes(escape(assertion), encoding='utf-8')
        assert assertion in response.data


@pytest.mark.parametrize('name, description, assertion',
                          [("Liverpool FC", "Will win the champions league", "success"),
                           ("Shannon's Bees", "yet more honeybees", "Name is already registered"),
                           ("Everton FC","", 'Description is required'),
                           ("", "Posh football team in London", "Group name is required")])
def test_groupcreate(test_client, test_db, name, description, assertion):
        """Test group create view.
        scenarios:
        test_client: test_client from conftest
        test_db: Test db from conftest
        normal group add, group already in db, 2x missing required fields.
        name: Name of group being added.
        description: Description of group being added.
        assertion: result being tested for.
        """
        login(test_client, "jjones", "password")
        test_case = {"name": name, "description": description}
        response = groupcreate(test_client, test_case)
        assertion = bytes(escape(assertion), encoding='utf-8')
        assert assertion in response.data