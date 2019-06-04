from app.models import User, Group
from flask import escape, url_for
from flask_login import current_user
import pytest
from .test_auth import login

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

def test_network(test_client, test_db):
    login(test_client, "jjones", "password")
    response = network(test_client)
    print(response.data.decode())
    assert '<li> <a href="/user/sarahsmith"> Sarah Smith </a></li>' in response.data.decode()
    assert '<li>Qhiv Hoa</li>' in response.data.decode()
    assert b'Mark Johnson' not in response.data
    assert '<form id = "modal_form_group" action="" method="POST">' in response.data.decode()
    assert response.data.decode().count("Qhiv Hoa") == 1


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