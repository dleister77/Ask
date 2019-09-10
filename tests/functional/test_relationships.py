import pytest
import re

from flask import escape, url_for
from flask_login import current_user

from app.models import User, Group, GroupRequest, FriendRequest
from app.utilities.email import get_token

from tests.conftest import scenarioUpdate, login, logout, FunctionalTest



class TestGroups(FunctionalTest):

    routeFunction = 'relationship.network_groups'

    def test_get(self, activeClient):
        assert len(current_user.groups) == 1
        testGroup = current_user.groups[0]
        response = self.getRequest(activeClient)
        assert response.status_code == 200
        testGroupLink = url_for('relationship.group', 
                                name=testGroup.name, id=testGroup.id)
        assert testGroupLink.encode() in response.data
        pendingCount = b"Pending<span>(0)</span>"
        assert pendingCount in response.data
        modalShow = b"$(modal).modal('show')"
        assert modalShow not in response.data

    def test_withPendingApproval(self, activeClient, testUser2):
        GroupRequest.create(group_id=1, requestor_id=testUser2.id)
        response = self.getRequest(activeClient)
        pendingCount = b"Pending<span>(1)</span>"
        assert pendingCount in response.data

    def tests_withPendingRequest(self, activeClient):
        GroupRequest.create(group_id=3, requestor_id=current_user.id)
        response = self.getRequest(activeClient)
        pendingCount = b"Pending<span>(1)</span>"
        assert pendingCount in response.data        

class TestFriends(FunctionalTest):

    routeFunction = 'relationship.network_friends'

    def test_get(self, activeClient):
        assert len(current_user.friends) == 1
        testFriend = current_user.friends[0]
        response = self.getRequest(activeClient)
        assert response.status_code == 200
        testFriendLink = url_for('main.user', username=testFriend.username)
        assert testFriendLink.encode() in response.data
        pendingCount = b"Pending<span>(0)</span>"
        assert pendingCount in response.data
        modalShow = b"$(modal).modal('show')"
        assert modalShow not in response.data
    
    def test_withPendingReceivedRequestApproval(self, activeClient, testUser3):
        FriendRequest.create(requestor_id=testUser3.id, friend_id=current_user.id)
        response = self.getRequest(activeClient)
        assert response.status_code == 200
        pendingCount = b"Pending<span>(1)</span>"
        assert pendingCount in response.data
        page = response.data.decode()
        sentRequests = r'<h5>Sent</h5>\s*<ul>\s*<li>None</li>\s*</ul>'
        match = re.search(sentRequests, page)
        assert match is not None
        recRequest = r'<h5>Received[\s\S]*<ul class="nobullets" id="name"><li><input\s*id="name-0" name="name" type="checkbox" value="1">\s*<label for="name-0">Mark Johnson</label>'
        match = re.search(recRequest, page)
        assert match is not None

    def test_withPendingSentRequestApproval(self, activeClient, testUser3):
        FriendRequest.create(requestor_id=current_user.id, friend_id=testUser3.id)
        response = self.getRequest(activeClient)
        page = response.data.decode()
        assert response.status_code == 200
        pendingCount = b"Pending<span>(1)</span>"
        assert pendingCount in response.data
        sentRequests = r'<h5>Sent</h5>\s*<ul>\s*<li>Mark Johnson</li>\s*</ul>'
        match = re.search(sentRequests, page)
        assert match is not None
        recRequests = r'<h5>Received</h5>\s*<ul>\s*<li>None</li>\s*</ul>'
        match = re.search(sentRequests, page)
        assert match is not None

class TestFriendAdd(FunctionalTest):

    routeFunction = 'relationship.friendadd'

    def test_new(self, activeClient, baseFriendSearch):
        self.form = baseFriendSearch
        response = self.postRequest(activeClient)
        page = response.data.decode()
        assert response.status_code == 200
        flash = f"Friend request sent to {baseFriendSearch['name']}.  Awaiting confirmation.".encode()
        assert flash in response.data
        assert response.status_code == 200
        pendingCount = b"Pending<span>(1)</span>"
        assert pendingCount in response.data
        sentRequests = r'<h5>Sent</h5>\s*<ul>\s*<li>Mark Johnson</li>\s*</ul>'
        match = re.search(sentRequests, page)
        assert match is not None
    
    def test_formError(self, activeClient, baseFriendSearch):
        baseFriendSearch.update({"id": len(User.query.all()) + 1})
        self.form = baseFriendSearch
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        flash = b'Friend request unsucessful.  Please correct errors and resubmit.'
        assert flash in response.data
        errorMsg = b'Person does not exist, please choose a different person to add.'
        assert errorMsg in response.data
        pendingCount = b"Pending<span>(0)</span>"
        assert pendingCount in response.data

class TestFriendApprove(FunctionalTest):

    routeFunction = 'relationship.friend_approve'

    def test_new(self, activeClient, testFriendrequest):
        self.form = {"name": [testFriendrequest.id]}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = f"You are now friends with {testFriendrequest.requestor.full_name}."
        assert flash.encode() in response.data
    
    def test_new_multiple(self, activeClient, testUser3, testUser4):
        request1 = FriendRequest.create(requestor_id=testUser3.id, friend_id=current_user.id)
        request2 = FriendRequest.create(requestor_id=testUser4.id, friend_id=current_user.id)
        self.form = {"name": [request1.id, request2.id]}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        print(response.data.decode())
        flash = escape(f"You are now friends with {request1.requestor.full_name} & {request2.requestor.full_name}.")
        assert flash.encode() in response.data

    def test_invalidID(self, activeClient, testFriendrequest):
        self.form = {"name": [100]}
        response = self.postRequest(activeClient)
        assert response.status_code == 422      
        flash = f"Request to add friend failed.  Please correct errors and resubmit."
        assert flash.encode() in response.data
        errorMsg = 'Please select name from the list.'
        print(response.data.decode())
        assert errorMsg.encode() in response.data

class TestFriendRemove(FunctionalTest):

    routeFunction = 'relationship.friend_remove'

    def test_remove1(self, activeClient, testUser2):
        assert len(current_user.friends) == 1
        self.form = {"name": [testUser2.id]}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = f"{testUser2.full_name} has been removed from your friends"
        assert flash.encode() in response.data
        assert len(current_user.friends) == 0

    def test_removeMultiple(self, activeClient, testUser2, testUser4):
        current_user.add(testUser4)
        assert len(current_user.friends) == 2
        self.form = {"name": [testUser2.id, testUser4.id]}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = f"{testUser2.full_name}, {testUser4.full_name} have been removed from your friends"
        assert flash.encode() in response.data
        assert len(current_user.friends) == 0

    def test_invalid(self, activeClient, testUser4):
        assert len(current_user.friends) == 1        
        self.form = {"name": [testUser4.id]}
        response = self.postRequest(activeClient)
        assert len(current_user.friends) == 1
        assert response.status_code == 422
        flash = f"Invalid request. Please correct errors and resubmit."
        assert flash.encode() in response.data
        errorMsg = 'Please select friend from list.'
        assert errorMsg.encode() in response.data

class TestFriendSearch(FunctionalTest):

    routeFunction = 'relationship.friendsearch'

    def test_valid(self, activeClient, testUser3):
        testCase = {"name": "mar"}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        check = [{"id": testUser3.id, 
              "first_name": testUser3.first_name, 
              "last_name": testUser3.last_name,
              "city": testUser3.address.city,
              "state": testUser3.address.state.state_short}]
        assert check == response.json

    def test_multiple(self, activeClient, testUser3, testUser4):
        testCase = {"name": "ma"}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        
        checkUsers = [testUser3, testUser4]
        check = []
        for user in checkUsers:
            check.append({"id": user.id, 
              "first_name": user.first_name, 
              "last_name": user.last_name,
              "city": user.address.city,
              "state": user.address.state.state_short})
        assert check == response.json

class TestFriendVerifyToken(FunctionalTest):

    routeFunction = 'relationship.friend_verify'

    def test_valid(self, activeClient, testFriendrequest):
        token = testFriendrequest._get_request_token()
        testCase = {"token": token}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        flash = f"You are now friends with {testFriendrequest.requestor.full_name}."
        assert flash.encode() in response.data
    
    def test_invalidtoken(self, activeClient, testFriendrequest):
        payload = {testFriendrequest.token_key : testFriendrequest.id}
        token = get_token(payload, -60)
        testCase = {"token": token}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        flash = "Friend request verification failed. Please either log in to submit new request or have requestor re-submit."
        assert flash.encode() in response.data        

class TestGroupProfile(FunctionalTest):

    routeFunction = 'relationship.group'

    def test_validAdmin(self, activeClient, testGroup):
        testCase = {"name": testGroup.name, "id": testGroup.id}
        response = self.getRequest(activeClient, **testCase)
        page = response.data.decode()
        assert response.status_code == 200
        updateForm = "id=groupUpdateForm"
        assert updateForm.encode() in response.data
        updateLink = '<a href="" class="btn btn-md btn-light ml-auto" data-toggle="modal" data-target="#groupUpdateForm">Edit</a>'
        assert updateLink.encode() in response.data
        assert testGroup.description.encode() in response.data
        for user in testGroup.members:
            link = url_for('main.user', username=user.username)
            check = re.compile(f'<li> <a href="{link}">\s*{user.full_name} </a></li>')
            assert check.search(page) is not None
    

    def test_validNonAdmin(self, activeClient, testGroup3):
        testCase = {"name": testGroup3.name, "id": testGroup3.id}
        response = self.getRequest(activeClient, **testCase)
        page = response.data.decode()
        assert response.status_code == 200
        updateForm = "id=groupUpdateForm"
        assert updateForm.encode() not in response.data
        updateLink = '<a href="" class="btn btn-md btn-light ml-auto" data-toggle="modal" data-target="#groupUpdateForm">Edit</a>'
        assert updateLink.encode() not in response.data    
    
    #TODO testcase for referrer
    def test_invalidWithReferrer(self, activeClient):
        testCase = {"name": "invalid", "id": 34}
        referrer = url_for('main.user', username='yardsmith')
        response = activeClient.get(url_for(self.routeFunction, **testCase,
                                            external=False),\
                                    follow_redirects=True,
                                    environ_base={"HTTP_REFERER": referrer})
        print(response.data.decode())
        assert b"Mark Johnson" in response.data

    def test_invalid(self, activeClient):
        testCase = {"name": "invalid", "id": 34}
        response = self.getRequest(activeClient, **testCase)
        page = response.data.decode()
        flash = "Invalid group requested."
        assert flash.encode() in response.data
        check = '<div id="network_groups"></div>'
        assert check.encode() in response.data

class TestGroupAdd(FunctionalTest):

    routeFunction = 'relationship.groupadd'

    def test_validGroupAdmin(self, activeClient, testGroup2):
        self.form = {"id": testGroup2.id}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = escape(f"Successfully added to {testGroup2.name}.")
        assert flash.encode() in response.data
        pendingCount = "Pending<span>(0)</span>"
        assert pendingCount.encode() in response.data

    def test_validNotAdmin(self, activeClient, testGroup3):
        self.form = {"id": testGroup3.id}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = f"Request sent to join {testGroup3.name}. Awaiting group admin confirmation."
        assert flash.encode() in response.data
        pendingCount = b"Pending<span>(1)</span>"
        assert pendingCount in response.data

    def test_invalidGroup(self, activeClient):
        self.form = {"id": len(Group.query.all()) + 1}
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        nextPageElement = '<div id="groupSearch"></div>'
        assert nextPageElement.encode() in response.data
        flash = 'Group does not exist, please choose a different group to add.'
        assert flash.encode() in response.data

class TestGroupApprove(FunctionalTest):

    routeFunction = 'relationship.group_approve'

    def test_valid(self, activeClient, testGroupRequest):
        self.form = {"request": [testGroupRequest.id]}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = f"{testGroupRequest.requestor.full_name} is now a member of {testGroupRequest.group.name}."
        assert flash.encode() in response.data

    def test_validMultiple(self, activeClient, testGroup, testUser2, testUser4):
        assert len(testGroup.members) == 2
        gr1 = GroupRequest.create(group_id=testGroup.id, requestor_id=testUser2.id)
        gr2 = GroupRequest.create(group_id=testGroup.id, requestor_id=testUser4.id)
        self.form = {"request": [gr1.id, gr2.id]}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        assert len(testGroup.members) == 4
        flash = f"{gr1.requestor.full_name} is now a member of {gr1.group.name}."
        assert flash.encode() in response.data
        flash2 = f"{gr2.requestor.full_name} is now a member of {gr2.group.name}."
        assert flash2.encode() in response.data        

    def test_invalid(self, activeClient):
        self.form = {"request": [100]}
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        flash = "Request to approve new group members failed. Please correct errors and try again."
        assert flash.encode() in response.data

class TestGroupCreate(FunctionalTest):

    routeFunction = "relationship.group_create"

    def test_emailNotVerified(self, activeClient, baseGroupNew):
        assert len(Group.query.all()) == 3
        self.form = baseGroupNew
        response = self.postRequest(activeClient)
        newGroup = Group.query.filter_by(name=baseGroupNew['name']).first()
        assert response.status_code == 200
        flash1 = 'Create new group disabled. Please verify email to unlock.'
        flash2 = 'Email address not yet verified. Please check email and confirm email address.'
        assert flash1.encode() in response.data
        assert flash2.encode() in response.data


    def test_valid(self, activeClient, baseGroupNew):
        current_user.email_verified = True
        assert len(Group.query.all()) == 3
        self.form = baseGroupNew
        response = self.postRequest(activeClient)
        print(response.data.decode())
        newGroup = Group.query.filter_by(name=baseGroupNew['name']).first()
        assert response.status_code == 200        
        assert len(Group.query.all()) == 4
        assert current_user in newGroup.members
        flash = escape(f"Successfully created {newGroup.name} and added you as member.")
        assert flash.encode() in response.data
    
    def test_invalidForm(self, activeClient, baseGroupNew):
        current_user.email_verified = True
        assert len(Group.query.all()) == 3
        baseGroupNew.update({"description": ""})
        self.form = baseGroupNew
        response = self.postRequest(activeClient)
        newGroup = Group.query.filter_by(name=baseGroupNew['name']).first()
        assert response.status_code == 422        
        assert len(Group.query.all()) == 3
        flash = "Group creation failed.  Please correct errors and resubmit."
        assert flash.encode() in response.data        

class TestGroupRemove(FunctionalTest):
    
    routeFunction = 'relationship.group_remove'

    def test_new(self, activeClient, testGroup):
        assert testGroup in current_user.groups
        self.form = {"name": testGroup.id}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        assert testGroup not in current_user.groups
        flash = f"{testGroup.name} has been removed from your groups"
        assert flash.encode() in response.data
        testGroupLink = url_for('relationship.group', 
                                name=testGroup.name, id=testGroup.id)
        assert testGroupLink.encode() not in response.data        

    def test_invalid(self, activeClient):
        self.form = {"name":len(Group.query.all())}
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        flash = "Failed to remove group(s). Please correct errors and resubmit."
        assert flash.encode() in response.data
        errorMsg = "Please select a group from the list."
        assert errorMsg.encode() in response.data

class TestGroupSearchAutocomplete(FunctionalTest):

    routeFunction = 'relationship.groupSearchAutocomplete'

    def test_valid(self, activeClient, testGroup):
        testCase = {"name": "q"}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        check = [{"id": testGroup.id, "name":testGroup.name}]
        assert check == response.json

class TestGroupSearch(FunctionalTest):

    routeFunction = 'relationship.groupSearch'

    def test_validMember(self, activeClient, testGroup):
        testCase = {"name": "qhiv"}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        url = url_for('relationship.group', name=testGroup.name, id=testGroup.id)
        groupLink = f'<a href="{url}">'
        assert groupLink.encode() in response.data

    def test_validNotMember(self, activeClient, testGroup3):
        testCase = {"name": "Sh"}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200        

    def test_invalid(self, activeClient, testGroup):
        testCase = {"name": ""}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 422
        errorMsg = 'Group name is required.'
        assert errorMsg.encode() in response.data
    
class TestGroupUpdate(FunctionalTest):

    routeFunction = 'relationship.groupUpdate'

    def test_valid(self, activeClient, testGroup):
        current_user.email_verified = True
        self.form = {"name": "Updated Name",
                    "description": "changed name",
                    "id": 1}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = "Group information updated"
        assert flash.encode() in response.data

    def test_validEmailNotVerified(self, activeClient):
        self.form = {"name": "Updated Name",
                    "description": "changed name",
                    "id": 1}
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        flash = "Form disabled. Please verify email to unlock."
        assert flash.encode() in response.data

    def test_validNotGroupAdmin(self, activeClient):
        current_user.email_verified = True
        self.form = {"name": "Updated Name",
                    "description": "changed name",
                    "id": 3}
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        flash = "Group information update failed.  User not authorized to make changes."
        assert flash.encode() in response.data        

    def test_invalid(self, activeClient):
        current_user.email_verified = True
        self.form = {"name": "",
                    "description": "changed name",
                    "id": 1}
        response = self.postRequest(activeClient)
        assert response.status_code == 422
        flash = "Group information update failed.  Please correct errors."
        assert flash.encode() in response.data
        errorMsg = "Group name is required."
        assert errorMsg.encode() in response.data

class TestGroupVerifyToken(FunctionalTest):

    routeFunction = 'relationship.group_verify'

    def test_valid(self, activeClient, testGroupRequest):
        token = testGroupRequest._get_request_token()
        testCase = {"token": token}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        flash = f"{testGroupRequest.requestor.full_name} is now a member of {testGroupRequest.group.name}."
        assert flash.encode() in response.data
    
    def test_invalidtoken(self, activeClient, testGroupRequest):
        payload = {testGroupRequest.token_key : testGroupRequest.id}
        token = get_token(payload, -60)
        testCase = {"token": token}
        response = self.getRequest(activeClient, **testCase)
        assert response.status_code == 200
        flash = "Group request verification failed. Please have requestor "\
               "re-submit."
        assert flash.encode() in response.data  