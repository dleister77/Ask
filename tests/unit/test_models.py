from collections import namedtuple
import datetime
from decimal import Decimal
import os
from pathlib import Path
import pytest
from shutil import rmtree

from flask import current_app
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from app import mail
from app.models import User, Address, Group, Category, Review, Provider,\
                       FriendRequest, GroupRequest, Sector, Picture, Message,\
                       Message_User, Conversation, Provider_Suggestion,\
                       Address_Suggestion
from app.utilities.email import get_token
from app.utilities.geo import AddressError, Location
from tests.conftest import assertEqualsTolerance


def null_test(test_db, model_class, test_case, key):
    """Test instance creation for required fields."""
    # instance = model_class.create(**test_case)
    # assert instance is not None
    # instance.delete()
    test_case[key] = None
    with pytest.raises(IntegrityError):
        model_class.create(**test_case)


@pytest.mark.usefixtures('dbSession')
class TestUser(object):
    """Tests for User model class."""

    def test_attributes(self):
        """
        GIVEN a User, Address model
        WHEN a new User is created
        THEN check the email, hashed_password, address, are set correctly.
        """
        u = User.query.filter_by(username="jjones").first()
        assert u.username == "jjones"
        assert u.email == "jjones@yahoo.com"
        assert len(u.reviews) == 4
        assert u.email_verified is False
        assert u._email_token_key == 'verify_email'
        assert u._password_token_key == 'reset_password'
        assert u.sentfriendrequests == []
        assert u.receivedfriendrequests == []
        assert u.sentgrouprequests == []
        u2 = User.query.get(1)
        assert u2 in u.friends
        assert type(u.address) == Address

    def test_newSameEmail(self):
        with pytest.raises(IntegrityError):
            User.create(
                first_name="Roberto", last_name="Firmino",
                email="jjones@yahoo.com", username="lfclegend"
            )

    def test_newSameUsername(self):
        with pytest.raises(IntegrityError):
            User.create(
                first_name="Roberto", last_name="Firmino",
                email="rfirmino@lfc.com", username="yardsmith"
            )

    @pytest.mark.parametrize(
        'key', ['first_name', 'last_name', 'username', 'email']
    )
    def test_newMissingRequired(self, newUserDict, key):
        newUserDict[key] = None
        with pytest.raises(IntegrityError):
            User.create(**newUserDict)

    @pytest.mark.parametrize(
        'key', ['first_name', 'last_name', 'username', 'email']
    )
    def test_newMissingEmptyString(self, newUserDict, key):
        newUserDict[key] = ''
        with pytest.raises(IntegrityError):
            User.create(**newUserDict)

    @pytest.mark.parametrize('key', ['address'])
    def test_newMissingAddress(self, newUserDict, key):
        newUserDict[key] = None
        with pytest.raises(AssertionError):
            User.create(**newUserDict)

    def test_update(self, testUser):
        testUser.update(first_name="Jurgen", last_name="Klopp",
                        email="coachinggod@lfc.com", username="jklopp")
        assert testUser.first_name == "Jurgen"
        assert testUser.last_name == "Klopp"
        assert testUser.email == "coachinggod@lfc.com"
        assert testUser.username == "jklopp"

    def test_updateSingleField(self, testUser):
        testUser.update(first_name="Jurgen")
        assert testUser.first_name == "Jurgen"

    def test_updateMissingInformation(self, testUser):
        with pytest.raises(IntegrityError):
            testUser.update(first_name=None, last_name="Klopp")

    def test_updateDuplicateInformation(self, testUser):
        with pytest.raises(IntegrityError):
            testUser.update(username="yardsmith")

    def test_checkUpdateSingleField(self, testUser):
        assert testUser.first_name != "Jurgen"

    def test_delete(self, testUser):
        FriendRequest.create(requestor_id=testUser.id, friend_id=4)
        GroupRequest.create(requestor_id=testUser.id, group_id=2)
        assert testUser.address.user_id == 2
        assert len(User.query.all()) == 4
        assert len(testUser.reviews) == 4
        assert len(Review.query.all()) == 7
        assert len(FriendRequest.query.all()) == 1
        assert len(GroupRequest.query.all()) == 1
        testUser.delete()
        testUser = User.query.get(2)
        assert testUser is None
        assert Review.query.filter_by(user_id=2).all() == []
        assert FriendRequest.query.filter_by(requestor_id=2).all() == []
        assert GroupRequest.query.filter_by(requestor_id=2).all() == []
        assert len(User.query.all()) == 3

    def test_checkPassword(self, testUser):
        assert testUser.check_password("password") is True
        assert testUser.check_password("liverpoolfc") is False

    def test_setPassword(self, testUser):
        testUser.set_password("longpassword")
        assert testUser.check_password("longpassword") is True

    def test_summary(self, testUser):
        assert testUser.summary().average == 4
        assert testUser.summary().count == 3
        testCost = (8/3)
        assert (testCost - .0001) <= testUser.summary().cost <= (testCost + .0001)

    def test_addFriend(self, testUser, testUser4):
        assert len(testUser.receivedfriendrequests) == 0
        request = FriendRequest.create(
            friend_id=testUser.id, requestor_id=testUser4.id
        )
        assert len(testUser.receivedfriendrequests) == 1
        assert len(testUser4.sentfriendrequests) == 1
        testUser.add(testUser4, request)
        assert testUser4 in testUser.friends
        assert len(testUser.receivedfriendrequests) == 0
        assert len(testUser4.sentfriendrequests) == 0

    def test_removeFriend(self, testUser, testUser2, testUser3):
        testUser.remove(testUser2)
        assert testUser2 not in testUser.friends
        with pytest.raises(ValueError):
            testUser.remove(testUser3)

    def test_addGroup(self, testUser):
        assert(len(testUser.groups) == 1)
        assert(len(testUser.sentgrouprequests) == 0)
        testGroup = Group.query.get(2)
        request = GroupRequest.create(group_id=2, requestor_id=2)
        assert len(testUser.sentgrouprequests) == 1
        testUser.add(testGroup, request)
        assert len(testUser.sentgrouprequests) == 0
        assert testGroup in testUser.groups

    def test_removeGroup(self, testUser):
        assert(len(testUser.groups) == 1)
        testGroup = Group.query.get(1)
        testUser.remove(testGroup)
        assert testGroup not in testUser.groups
        assert len(testUser.groups) == 0
        with pytest.raises(ValueError):
            testUser.remove(testGroup)

    def test_sendEmailVerification(self, testUser):
        """Test sending of email verification emails."""
        with mail.record_messages() as outbox:
            testUser.send_email_verification()
            assert len(outbox) == 1
            msg = outbox[0]
            assert "jjones@yahoo.com" in msg.recipients
            assert msg.subject == 'Ask Your Peeps: Email Verification'
            assert 'To verify your email' in msg.body
            assert 'Dear John' in msg.body

    def test_verifyEmailToken(self, testUser):
        """Test verification of email tokens along with error codes."""
        test_token = testUser._get_email_verification_token()
        resulting_user, error = User.verify_email_verification_token(test_token)
        assert resulting_user == testUser
        assert error is None

    def test_verifyEmailTokenExpired(self, testUser):
        test_token = testUser._get_email_verification_token(expiration=-200)
        resulting_user, error = User.verify_email_verification_token(test_token)
        assert resulting_user is None
        assert error == "Expired"
        test_token = "xjdkldfj1893.xdkld.jfkdl"
        resulting_user, error = User.verify_email_verification_token(test_token)
        assert resulting_user is None
        assert error == "Invalid"

    def test_passwordTokens(self, base_user):
        """Test pwd reset token generation and verification."""
        test_user = User.query.filter_by(username=base_user['username'])\
            .first()
        alt_user = User.query.get(1)
        with mail.record_messages():
            t = test_user._get_reset_password_token()
            u = User.verify_password_reset_token(t)
            assert u == test_user
            t2 = alt_user._get_reset_password_token()
            u = User.verify_password_reset_token(t2)
            assert u == alt_user
            assert u != test_user

    def test_sendPasswordResetEmail(self, testUser):
        """Test sending of password reset emails."""
        with mail.record_messages() as outbox:
            testUser.send_password_reset_email()
            assert len(outbox) == 1
            msg = outbox[0]
            assert "jjones@yahoo.com" in msg.recipients
            assert msg.subject == 'Ask Your Peeps: Password Reset'
            assert 'To reset your password, please paste the below link into'\
                ' your browser' in msg.body


@pytest.mark.usefixtures("dbSession")
class TestAddress(object):
    """Test address class in model"""
    def test_attributes(self, testUser):
        address = testUser.address
        assert address.line1 == "7708 Covey Chase Dr"
        assert address.city == "Charlotte"
        assert address.city != "charlotte"
        assert address.state.name == "North Carolina"
        assert address.zip == "28210"
        assert address.unknown is False
        assert address.user_id == 2
        assertEqualsTolerance(address.longitude, -80.864783, 5)
        assertEqualsTolerance(address.latitude, 35.123949, 5)

    @pytest.mark.parametrize('key', ['city', 'state_id'])
    def test_newMissingRequired(self, key, newAddressDict, mockGeoResponse):
        newAddressDict[key] = None
        with pytest.raises(IntegrityError):
            Address.create(**newAddressDict)

    @pytest.mark.parametrize('key', ['city', 'state_id'])
    def test_newRequiredEmptyString(self, key, newAddressDict, mockGeoResponse):
        newAddressDict[key] = ""
        with pytest.raises(IntegrityError):
            Address.create(**newAddressDict)

    @pytest.mark.parametrize('key', ['line1', 'zip'])
    def test_missingRequiredUnknownFalse(self, key, newAddressDict,
                                         mockGeoResponse):
        newAddressDict[key] = None
        with pytest.raises(AssertionError):
            Address.create(**newAddressDict)

    def test_unknownTrue(self, newAddressDict, mockGeoResponse):
        newAddressDict.update({
            'unknown': True, 'line1': None, 'zip': None, 'user_id': None
        })
        address = Address(**newAddressDict)
        assert address is not None
        assert address.city == newAddressDict['city']

    def test_getCoordinatesMock(self, testUser, mockGeoResponse):
        address = testUser.address
        assert address.line1 == "7708 Covey Chase Dr"
        address.line1 = "8012 Covey Chase Dr"
        address.get_coordinates()
        assert address.latitude == 35.119714
        assert address.longitude == -80.865332

    def test_newInvalid(self, testUser, mockGeoResponse):
        with pytest.raises(AddressError):
            Address(
                line1="1 covey chase dr", city="Charlotte",
                state_id=1, user_id=1, zip="28210"
            )

    def test_updateValid(self, activeClient, testUser, mockGeoResponse):
        assert testUser.address.line1 == "7708 Covey Chase Dr"
        assertEqualsTolerance(testUser.address.longitude, -80.864783, 5)
        assertEqualsTolerance(testUser.address.latitude, 35.123949, 5)
        testUser.address.update(
            line1="8012 Covey Chase Dr", city="Belmont", zip="28212"
        )
        assert testUser.address.line1 == "8012 Covey Chase Dr"
        assertEqualsTolerance(testUser.address.longitude, -80.865332, 5)
        assertEqualsTolerance(testUser.address.latitude, 35.119714, 5)

    def test_updateInvalid(self, testUser, mockGeoResponse):
        with pytest.raises(AddressError):
            testUser.address.update(line1="1 covey chase dr")

    def test_noOrphanAddress(self, testUser4):
        with pytest.raises(AssertionError):
            testUser4.address.update(user=None)

    def test_noOrphanAddress2(self, testUser4):
        with pytest.raises(AssertionError):
            testUser4.update(address=None)

    def test_userDeleteCascade(self, testUser4):
        address = testUser4.address
        assert address.id == 4
        assert address.user_id == 4
        assert address.provider_id is None
        testUser4.delete()
        assert Address.query.get(4) is None

    def test_providerDeleteCascade(self, testProvider1):
        assert testProvider1.address.id == 5
        testProvider1.delete()
        assert Address.query.get(5) is None


@pytest.mark.usefixtures("dbSession")
class TestFriendRequest(object):
    def test_new(self, testUser, testUser4, testFriendrequest):
        assert testFriendrequest in testUser4.sentfriendrequests
        assert testFriendrequest in testUser.receivedfriendrequests
        assert testFriendrequest.requestor == testUser4
        assert testFriendrequest.requested_friend == testUser

    def test_send(self, testUser, testUser4, testFriendrequest):
        with mail.record_messages() as outbox:
            testFriendrequest.send()
            assert len(outbox) == 1
            msg = outbox[0]
            assert testUser.email in msg.recipients
            assert msg.subject == 'Ask Your Peeps: Friend Verification'
            assert f"{testUser4.full_name} would like to be friends with you "\
                "on Ask Your Peeps" in msg.body

    def test_verifyValid(self, testFriendrequest):
        testToken = testFriendrequest._get_request_token()
        check = testFriendrequest.verify_token(testToken)
        assert check == testFriendrequest

    def test_verifyInvalid(self, testFriendrequest):
        payload = {"request": 2}
        testToken = get_token(payload, None)
        check = testFriendrequest.verify_token(testToken)
        assert check is None


@pytest.mark.usefixtures("dbSession")
class TestGroupRequest(object):
    def test_new(self, testUser4, testGroup, testGroupRequest):
        assert testGroupRequest in testUser4.sentgrouprequests
        assert testGroupRequest in testGroup.join_requests
        assert testGroupRequest.requestor == testUser4
        assert testGroupRequest.group == testGroup

    def test_send(self, testUser4, testGroup, testGroupRequest):
        with mail.record_messages() as outbox:
            assert len(outbox) == 0
            testGroupRequest.send()
            assert len(outbox) == 1
            msg = outbox[0]
            assert "jjones@yahoo.com" in msg.recipients
            assert msg.subject == "Ask Your Peeps: Group Join Request"
            assert f"{testUser4.full_name} would like to join "\
                f"{testGroup.name} on Ask Your Peeps" in msg.body

    def test_getPending(self, testUser, testGroupRequest):
        pending = GroupRequest.get_pending(testUser)
        assert len(pending) == 1
        assert testGroupRequest in pending


@pytest.mark.usefixtures("dbSession")
class TestSector(object):
    """Test sector model class."""
    def test_attributes(self):
        sector = Sector.query.get(1)
        assert sector.name == 'Home Services'
        assert sector.categories == Category.query.filter_by(sector_id=1).all()

    def test_list(self):
        testList = Sector.list()
        assert testList == [(1, 'Home Services'), (2, 'Food & Drink')]


@pytest.mark.usefixtures("dbSession")
class TestCategory(object):
    def test_attributes(self):
        testCategory = Category.query.get(1)
        assert testCategory.name == 'Electrician'
        assert len(testCategory.reviews) == 7
        assert len(testCategory.providers) == 4
        assert testCategory.sector.name == 'Home Services'

    def test_categoryList(self):
        sector_id = 1
        testList = Category.list(sector_id)
        assert len(testList) == 2
        assert (1, 'Electrician') in testList
        assert (2, 'Plumber') in testList


@pytest.mark.usefixtures("dbSession")
class TestProvider(object):

    def generateSearchFilters(self, searchDict):
        """From dict, populate filters used in call to Provider.search"""

        location = Location(searchDict['location'])
        location.setRangeCoordinates(searchDict['searchRange'])
        category = Category.query.get(searchDict['category'])
        filters = {
            "name": searchDict['name'],
            "category": category,
            "location": location,
            "reviewed": bool(searchDict['reviewed_filter']),
            "friends": bool(searchDict['friends_filter']),
            "groups": bool(searchDict['groups_filter'])
        }
        sort = searchDict['sort']
        return filters, sort

    def test_attributes(self, testProvider):
        assert testProvider.name == "Douthit Electrical"
        assert testProvider.email == "douthit@gmail.com"
        assert testProvider.website == 'www.douthitelectrical.com/'
        assert testProvider.telephone == "7047263329"
        assert testProvider.address.line1 == "6000 Fairview Rd"
        assert testProvider.is_active is True

    def test_newValid(self, newProviderDict, newAddressDict, mockGeoResponse):
        new = Provider.create(**newProviderDict)
        assert new.name == newProviderDict['name']
        assert new.email == newProviderDict['email']

    @pytest.mark.parametrize('key', ['name', 'telephone'])
    def test_newMissingRequired(self, newProviderDict, key):
        newProviderDict[key] = None
        with pytest.raises(IntegrityError):
            Provider.create(**newProviderDict)

    @pytest.mark.parametrize('key', ['address'])
    def test_newMissingAddress(self, newProviderDict, key):
        newProviderDict[key] = None
        with pytest.raises(AssertionError):
            Provider.create(**newProviderDict)

    @pytest.mark.parametrize('key', ['name', 'telephone'])
    def test_newMissingRequiredEmptyString(self, newProviderDict, key):
        newProviderDict[key] = ''
        with pytest.raises(IntegrityError):
            Provider.create(**newProviderDict)

    def test_newDuplicateEmail(self):
        with pytest.raises(IntegrityError):
            Provider.create(
                name="Test Provider",
                email="douthit@gmail.com",
                telephone="1234567891",
                categories=[Category.query.get(1)]
            )

    def test_newDuplicateNullEmail(self):
        Provider.create(
            name="Test Provider", telephone="1234567891", email='',
            categories=[Category.query.get(1)]
        )
        p = Provider.query.filter_by(name="Test Provider").first()
        assert p is not None

    def test_newDuplicateTelephone(self):
        with pytest.raises(IntegrityError):
            Provider.create(
                name="Test Provider", email="testemail@test.com",
                telephone="7047263329", categories=[Category.query.get(1)]
            )

    def test_updateValid(self, testProvider):
        assert testProvider.name == "Douthit Electrical"
        assert testProvider.email == "douthit@gmail.com"
        assert testProvider.telephone == "7047263329"
        testProvider.update(name="Don's Electric", email="don@aol.com",
                            telephone='7044103333')
        assert testProvider.name == "Don's Electric"
        assert testProvider.email == "don@aol.com"
        assert testProvider.telephone == '7044103333'

    def test_updateDuplicateEmail(self, testProvider):
        assert testProvider.email == "douthit@gmail.com"
        with pytest.raises(IntegrityError):
            testProvider.update(email="preferred@gmail.com")

    def test_updateDuplicateTelephone(self, testProvider):
        assert testProvider.telephone == "7047263329"
        with pytest.raises(IntegrityError):
            testProvider.update(telephone="7043470446")

    def test_listTuple(self, testProvider):
        categoryid = 1
        providers = Provider.list(categoryid)
        assert len(providers) == 3
        assert (testProvider.id, testProvider.name) in providers

    def test_providerListDict(self, testProvider):
        categoryid = 1
        providers = Provider.list(categoryid, 'dict')
        assert len(providers) == 3
        assert {"id": testProvider.id, "name": testProvider.name} in providers

    def test_searchNoName(self, activeClient, baseProviderSearch):
        # create filters, location, category

        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort)
        assert len(providers) == 3
        assert providers[0].name == 'Douthit Electrical'
        assert providers[1].name == 'Evers Electric'
        assert providers[2].name == 'Preferred Electric Co'
        assert providers[0].reviewAverage == (10/4)
        assert providers[0].reviewCount == 4
        assert providers[0].reviewCost == (18/4)
        assert providers[0].categories == "Electrician,Plumber"

    def test_searchShortDistance(self, activeClient, baseProviderSearch):
        baseProviderSearch.update({"searchRange": 7})
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort)
        assert len(providers) == 2
        assert providers[0].name == 'Douthit Electrical'
        assert providers[1].name == 'Preferred Electric Co'

    def test_searchName(self, activeClient, baseProviderSearch):
        baseProviderSearch['name'] = 'Evers Electric'
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort)
        assert providers[0].name == 'Evers Electric'
        assert providers[0].website == 'www.everselectric.com/'
        assert providers[0].reviewAverage is None
        assert providers[0].reviewCount == 0
        assert providers[0].reviewCost is None

    def test_searchRatingSort(self, activeClient, baseProviderSearch):
        baseProviderSearch['sort'] = 'rating'
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort)
        assert len(providers) == 3
        assert providers[0].name == 'Preferred Electric Co'
        assert providers[1].name == 'Douthit Electrical'
        assert providers[2].name == 'Evers Electric'
        assert providers[1].categories == "Electrician,Plumber"

    def test_searchLimit(self, activeClient, baseProviderSearch):
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        limit = 1
        providers = Provider.search(filters, sort=sort, limit=limit)
        assert len(providers) == 1
        assert providers[0].name == 'Douthit Electrical'
        assert providers[0].reviewAverage == (10/4)
        assert providers[0].reviewCount == 4
        assert providers[0].reviewCost == (18/4)

    def test_searchReviewed(self, activeClient, baseProviderSearch):
        baseProviderSearch['reviewed_filter'] = True
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort=sort)
        assert len(providers) == 2
        assert providers[0].name == 'Douthit Electrical'
        assert providers[1].name == 'Preferred Electric Co'

    def test_searchFriends(self, activeClient, baseProviderSearch):
        baseProviderSearch['friends_filter'] = True
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort=sort)
        assert len(providers) == 1
        assert providers[0].name == 'Douthit Electrical'
        assert providers[0].reviewAverage == 1
        assert providers[0].reviewCount == 2
        assert providers[0].reviewCost == 5
        assert providers[0].categories == "Electrician,Plumber"

    def test_searchGroups(self, activeClient, baseProviderSearch):
        baseProviderSearch['groups_filter'] = True
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort=sort)
        assert len(providers) == 1
        assert providers[0].name == 'Douthit Electrical'
        assert providers[0].reviewAverage == 5
        assert providers[0].reviewCount == 1
        assert providers[0].reviewCost == 5
        assert providers[0].categories == "Electrician,Plumber"

    def test_searchFriendsOrGroups(self, activeClient, baseProviderSearch):
        baseProviderSearch.update({
            "friends_filter": True, "groups_filter": True
        })
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        providers = Provider.search(filters, sort=sort)
        assert len(providers) == 1
        assert providers[0].name == 'Douthit Electrical'
        assertEqualsTolerance(providers[0].reviewAverage, (7/3), 3)
        assert providers[0].reviewCount == 3
        assert providers[0].reviewCost == 5
        assert providers[0].categories == "Electrician,Plumber"

    def test_profileNoFilter(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": False, "groups_filter": False}
        profile = testProvider.profile(reviewFilter)
        assert profile[0] == testProvider
        assertEqualsTolerance(profile[1], 2.5, 5)
        assertEqualsTolerance(profile[2], (18/4), 5)
        assert profile[3] == 4

    def test_profileFriends(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": True, "groups_filter": False}
        profile = testProvider.profile(reviewFilter)
        assert profile[0] == testProvider
        assert profile[1] == 1
        assert profile[2] == 5
        assert profile[3] == 2

    def test_profileGroups(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": False, "groups_filter": True}
        profile = testProvider.profile(reviewFilter)
        assert profile[0] == testProvider
        assert profile[1] == 5
        assert profile[2] == 5
        assert profile[3] == 1

    def test_profileGroupsandFriends(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": True, "groups_filter": True}
        profile = testProvider.profile(reviewFilter)
        assert profile[0] == testProvider
        assertEqualsTolerance(profile[1], (7/3), 3)
        assert profile[2] == 5
        assert profile[3] == 3


@pytest.mark.usefixtures("dbSession")
class TestReview(object):

    def generateSearchFilters(self, searchDict):
        """From dict, populate filters used in call to Provider.search"""

        location = Location(searchDict['location'])
        location.setRangeCoordinates(searchDict['searchRange'])
        category = Category.query.get(searchDict['category'])
        filters = {
            "name": searchDict['name'],
            "category": category,
            "location": location,
            "reviewed": bool(searchDict['reviewed_filter']),
            "friends": bool(searchDict['friends_filter']),
            "groups": bool(searchDict['groups_filter'])
        }
        sort = searchDict['sort']
        return filters, sort

    def test_attributes(self, testReview):
        assert testReview.user_id == 2
        assert testReview.provider.name == 'Douthit Electrical'
        assert testReview.category.name == 'Electrician'
        assert testReview.rating == 3
        assert testReview.cost == 3
        assert testReview.description == 'fixed a light bulb'
        assert testReview.comments == 'satisfactory work.'

    @pytest.mark.parametrize('key', ['provider', 'category', 'rating', 'cost'])
    def test_newMissingRequired(self, newReviewDict, key):
        newReviewDict[key] = None
        with pytest.raises(IntegrityError):
            Review.create(**newReviewDict)

    @pytest.mark.parametrize('key', ['provider', 'category', 'rating', 'cost'])
    def test_newMissingRequiredEmptyString(self, newReviewDict, key):
        newReviewDict[key] = ''
        with pytest.raises(IntegrityError):
            Review.create(**newReviewDict)

    def test_search(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": False, "groups_filter": False}
        reviews = Review.search(
            provider_id=testProvider.id, filter=reviewFilter
        )
        assert len(reviews) == 4
        rev_1 = list(filter(lambda r: r.id == 1, reviews))[0]
        assert rev_1.rating == 3
        assert rev_1.cost == 3
        assert rev_1.description == 'fixed a light bulb'

    def test_searchFriendFilter(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": True, "groups_filter": False}
        reviews = Review.search(
            provider_id=testProvider.id, filter=reviewFilter
        )
        assert len(reviews) == 2
        assert reviews[0].rating == 1
        assert reviews[0].cost == 5
        assert reviews[0].description == 'test'

    def test_searchGroupsFilter(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": False, "groups_filter": True}
        reviews = Review.search(
            provider_id=testProvider.id, filter=reviewFilter
        )
        assert len(reviews) == 1
        assert reviews[0].rating == 5
        assert reviews[0].cost == 5
        assert reviews[0].description == 'installed breaker box'

    def test_searchGroupsandFriends(self, testProvider, activeClient):
        reviewFilter = {"friends_filter": True, "groups_filter": True}
        reviews = Review.search(
            provider_id=testProvider.id, filter=reviewFilter
        )
        assert len(reviews) == 3
        assert reviews[0].rating == 5
        assert reviews[0].cost == 5
        assert reviews[0].description == 'installed breaker box'

    def test_searchGroup(self, testGroup, testUser3, activeClient):
        reviews = Review.search(group_id=testGroup.id)
        assert len(reviews) == 4
        review_ids = [1, 2, 4, 5]
        for r in review_ids:
            assert Review.query.get(r) in reviews

    def test_searchUser(self, testUser, activeClient):
        reviews = Review.search(user_id=testUser.id)
        assert len(reviews) == 3
        review_ids = [1, 4, 5]
        for r in review_ids:
            assert Review.query.get(r) in reviews

    def test_summaryStatSearch(self, activeClient, baseProviderSearch):
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        reviews = Review.summaryStatSearch(filters)
        assert reviews.count == 6
        assert reviews.average == round(Decimal(19/6), 4)
        assert reviews.cost == round(Decimal(23/6), 4)

    def test_summaryStatSearchGroups(self, activeClient, baseProviderSearch):
        baseProviderSearch['groups_filter'] = True
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        reviews = Review.summaryStatSearch(filters)
        assert reviews.count == 1
        assert reviews.average == round(Decimal(5), 4)
        assert reviews.cost == round(Decimal(5), 4)

    def test_summaryStatSearchFriends(self, activeClient, baseProviderSearch):
        baseProviderSearch['friends_filter'] = True
        filters, sort = self.generateSearchFilters(baseProviderSearch)
        reviews = Review.summaryStatSearch(filters)
        assert reviews.count == 2
        assert reviews.average == round(Decimal(1), 4)
        assert reviews.cost == round(Decimal(5), 4)


@pytest.mark.usefixtures("dbSession")
class TestGroup(object):
    def test_attributes(self, testGroup, testUser, testUser3):
        assert testGroup.name == 'QHIV HOA'
        assert testGroup.description == 'Hoa for the neighborhood'
        assert testGroup.admin == testUser
        assert testUser in testGroup.members
        assert testUser3 in testGroup.members
        assert len(testGroup.members) == 2

    def test_newRepeatName(self):
        with pytest.raises(IntegrityError):
            Group.create(name="QHIV HOA", description="test", admin_id=2)

    def test_update(self, testGroup):
        testGroup.update(name='Quail Hollow Estates', description='Testdescription')
        assert testGroup.name == 'Quail Hollow Estates'
        assert testGroup.description == 'Testdescription'

    def test_updateDuplicateName(self, testGroup):
        with pytest.raises(IntegrityError):
            testGroup.update(name="Shannon's Bees")

    def test_delete(self, testGroup, testUser, testUser3):
        assert testUser in testGroup.members
        id = testGroup.id
        testGroup.delete()
        assert Group.query.get(id) is None
        assert User.query.get(testUser.id) is not None

    def test_searchNotMember(self, testGroup2, activeClient):
        filters = {"name": "Shanno"}
        groups = Group.search(filters)
        assert len(groups) > 0
        assert groups[0].name == testGroup2.name
        assert groups[0].description == testGroup2.description
        assert groups[0].id == testGroup2.id
        assert groups[0].membership is False

    def test_searchMember(self, testGroup, activeClient):
        filters = {"name": "Qhi"}
        groups = Group.search(filters)
        assert len(groups) > 0
        assert groups[0].name == testGroup.name
        assert groups[0].description == testGroup.description
        assert groups[0].id == testGroup.id
        assert groups[0].membership is True


# mock test objects to replace wtf forms
form = namedtuple('form', ['picture', 'deletePictures'])
picture = namedtuple('picture', 'data')
deletePictures = namedtuple('deletePictures', 'data')


@pytest.mark.usefixtures("dbSession")
class TestPicture(object):
    def test_attributes(self, testReview):
        name = 'test.jpg'
        path = os.path.join(current_app.config['MEDIA_FOLDER'], name)
        testReview.update(pictures=[Picture(path=path, name=name)])
        assert testReview.pictures[0].path == path
        assert testReview.pictures[0].name == name

    def test_savePictures(self, activeClient):
        filename = "test.jpg"
        path = os.path.join(
            current_app.config['MEDIA_FOLDER'], 'source', filename
        )
        f = open(path, 'rb')
        fs = FileStorage(
            stream=f, filename=filename, content_type='image/jpeg'
        )
        testform = form(picture([fs]), None)
        try:
            Picture.savePictures(testform)
            path = Path(os.path.join(
                current_app.config['MEDIA_FOLDER'], str(current_user.id),
                filename
                )
            )
            check_path = Path(os.path.join(
                current_app.config['MEDIA_FOLDER'], str(current_user.id),
                f'{current_user.username}_1.jpg'
                )
            )
            assert check_path.is_file()
        finally:
            path = os.path.join(
                current_app.config['MEDIA_FOLDER'], str(current_user.id)
            )
            rmtree(path)

    def test_deletePictures(self, activeClient, testPicture):
        name = testPicture.name
        id = Picture.query.filter_by(name=name).first().id
        testform = form(None, deletePictures([id]))
        assert testPicture.is_file()
        Picture.deletePictures(testform)
        assert not testPicture.is_file()


@pytest.mark.usefixtures("dbSession")
class TestMessageUser(object):
    def test_recipient(self, test_recipient, testUser, test_message):
        assert test_recipient.tag == 'inbox'
        assert test_recipient.read is False
        assert test_recipient.role == 'recipient'
        assert test_recipient.user_id == 2
        assert test_recipient.message_id == 1
        assert test_recipient.full_name == testUser.full_name

    def test_sender(self, test_sender, testUser2, test_message):
        assert test_sender.tag == 'sent'
        assert test_sender.read is True
        assert test_sender.role == 'sender'
        assert test_sender.user_id == 1
        assert test_sender.message_id == 1
        assert test_sender.full_name == testUser2.full_name

    def test_delete_user(self, test_sender, testUser2, test_message):
        test_name = f'{testUser2.full_name}'
        assert test_sender.user_id == 1
        assert test_sender.message_id == 1
        assert test_sender.full_name == test_name
        testUser2.delete()
        assert test_sender.user_id is None
        assert test_sender.message_id == 1
        assert test_sender.full_name == test_name


@pytest.mark.usefixtures("dbSession")
class TestMessage(object):
    def test_attributes(self, test_message, test_sender, test_recipient):
        assert test_message.conversation_id == 1
        assert test_message.subject == "test subject"
        assert test_message.body == "test body"
        assert test_message.sender == test_sender
        assert test_message.recipient == test_recipient

    def test_send_new(self, testUser, testUser2):
        check = Message.send_new(
            dict(user_id=testUser2.id), dict(user_id=testUser.id), "test1",
            "test2"
        )
        assert check.subject == "test1"
        assert check.body == "test2"
        assert check.sender.user == testUser2
        assert check.sender.full_name == testUser2.full_name
        assert check.recipient.user == testUser
        assert check.recipient.full_name == testUser.full_name

    def test_delete_1_user(self, test_message, testUser2):
        assert test_message is not None
        assert test_message.sender.user == testUser2
        testUser2.delete()
        assert test_message is not None
        assert test_message.sender is not None
        assert test_message.sender.user is None

    def test_reply(self, test_message):
        m = test_message.send_reply("Re: Test", "Sending a reply")
        assert m.conversation_id == 1
        assert m.subject == "Re: Test"
        assert m.body == "Sending a reply"
        assert m.sender.user_id == test_message.recipient.user_id
        assert m.sender.full_name == test_message.recipient.full_name
        assert m.recipient.user_id == test_message.sender.user_id
        assert m.recipient.full_name == test_message.sender.full_name

    def test_send_admin(self, testUser):
        m = Message.send_admin(dict(user_id=2), "admin subject", "admin body")
        assert m.subject == "admin subject"
        assert m.sender.user == testUser
        assert m.msg_type == "admin"
        assert m.recipient.full_name == "AYP Admin"

    def test_send_admin_email(self, testUser):
        m = Message.send_admin(
            dict(full_name="John Smith", email="jsmith@smith.com"),
            "another admin subject", "more admin tests"
        )
        assert m.subject == "another admin subject"
        assert m.sender.email == "jsmith@smith.com"
        assert m.sender.full_name == "John Smith"
        assert m.msg_type == "admin"
        assert m.sender.user is None
        assert m.recipient.full_name == "AYP Admin"
        assert m.recipient.email == current_app.config['ADMINS'][0]

    def test_message_delete_cascade(self, test_message):
        s_id = int(test_message.sender.id)
        r_id = int(test_message.recipient.id)
        assert test_message is not None
        assert Message_User.query.get(s_id) is not None
        test_message.delete()
        assert Message_User.query.get(s_id) is None
        assert Message_User.query.get(r_id) is None
        assert Message.query.get(test_message.id) is None


@pytest.mark.usefixtures("dbSession")
class TestConversation(object):
    def test_attributes(self, test_message):
        c = test_message.conversation_id
        assert c is not None

    def test_delete_cascade(self, test_message):
        m_id = test_message.id
        c_id = test_message.conversation_id
        assert test_message is not None
        c = Conversation.query.get(c_id)
        c.delete()
        c = Conversation.query.get(c_id)
        assert c is None
        m = Message.query.get(m_id)
        assert m is None


@pytest.mark.usefixtures("dbSession", "activeClient")
class TestProviderSuggestion(object):
    def test_create(self, testProvider):
        c = Category.query.get(3)
        address = Address_Suggestion.create(
            line1="7708 Covey Chase Dr",
            line2="",
            city="Charlotte",
            state_id=1,
            zip="28210",
            is_coordinate_error=False,
        )
        suggestion = Provider_Suggestion.create(
            provider_id=testProvider.id,
            is_not_active=True,
            user_id=current_user.id,
            name="Joe's Electric",
            email="new_email_address@yahoo.com",
            address=address,
            categories=[c]
        )
        assert suggestion is not None
        assert suggestion.provider == testProvider
        assert suggestion.user == current_user
        assert suggestion.name == "Joe's Electric"
        assert suggestion.email == "new_email_address@yahoo.com"
        assert suggestion.is_contact_error is True
        assert suggestion.is_not_active is True
        assert suggestion.status == 'open'
        assert suggestion.is_address_error is True
        assert suggestion.is_category_error is True
        assert suggestion.timestamp.date() == datetime.date.today()
        assert address.provider_suggestion_id == suggestion.id
        assert suggestion.address.line1 == "7708 Covey Chase Dr"
        assert suggestion.address.is_coordinate_error is False
        assert suggestion.categories == [c]
        assert Address_Suggestion.query.first() == suggestion.address

    def test_delete_cascade(self, testProvider):
        c = Category.query.get(3)
        address = Address_Suggestion.create(
            line1="7708 Covey Chase Dr",
            line2="",
            city="Charlotte",
            state_id=1,
            zip="28210"
        )
        Provider_Suggestion.create(
            provider_id=testProvider.id,
            is_not_active=True,
            user_id=current_user.id,
            name="Joe's Electric",
            email="new_email_address@yahoo.com",
            address=address,
            categories=[c]
        )
        suggestions = Provider_Suggestion.query.all()
        assert len(suggestions) == 1
        testProvider.delete()
        suggestions = Provider_Suggestion.query.all()
        assert len(suggestions) == 0

    def test_invalid_status(self, testProvider):
        c = Category.query.get(3)
        address = Address_Suggestion.create(
            line1="7708 Covey Chase Dr",
            line2="",
            city="Charlotte",
            state_id=1,
            zip="28210",
            is_coordinate_error=False,
        )
        with pytest.raises(ValueError):
            Provider_Suggestion.create(
                provider_id=testProvider.id,
                is_not_active=True,
                user_id=current_user.id,
                name="Joe's Electric",
                status="excellent",
                email="new_email_address@yahoo.com",
                address=address,
                categories=[c]
        )