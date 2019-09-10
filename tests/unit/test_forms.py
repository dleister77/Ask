from flask import request
from flask_login import current_user
import pytest
from werkzeug.datastructures import ImmutableMultiDict
from wtforms import ValidationError

from app import create_app
from app.models import Sector, Category, Provider, FriendRequest, GroupRequest,\
	                   Group
from app.relationship.forms import (GroupCreateForm, FriendSearchForm,\
									GroupSearchForm, GroupEditForm,
									FriendDeleteForm, FriendApproveForm,
									GroupDeleteForm, GroupMemberApproveForm)
from app.utilities.geo import Location						
from tests.conftest import login, scenarioUpdate
from config import TestConfig

app = create_app(TestConfig)
with app.app_context():
	from app.main.forms import ProviderAddForm, ProviderSearchForm, ReviewForm,\
		                       ProviderFilterForm, ProviderAddress
	from app.auth.forms import UserUpdateForm, PasswordChangeForm,\
							   RegistrationForm, LoginForm, AddressField,\
							   PasswordResetForm, PasswordResetRequestForm

@pytest.mark.usefixtures("dbSession")
class FormTest(object):

	formType = ProviderAddForm
	form = None
	formDict = None
		
	def make_form(self, formDict):
		"""Helper method to generate Provider form for tests."""
		self.formDict = formDict
		formDictImmut = ImmutableMultiDict(self.formDict)
		self.form = self.formType(formdata=formDictImmut)

	def assertNot(self, key, errorMsg):
		"""Helper assertion to check not validating and confirm error message."""
		assert not self.form.validate()
		assert errorMsg in self.form.errors[key]

	def new(self, formDict):
		self.make_form(formDict)
		assert self.form.validate()

	def missingRequired(self, formDict, key, errorMsg):
		formDict.pop(key)
		self.make_form(formDict)
		self.assertNot(key, errorMsg)

def make_form(formClass, providerDict):
	form = ImmutableMultiDict(providerDict)
	form = formClass(formdata=form)
	return form


def form_test(test_app, test_form, test_case):
	"""Test form validation.
	test_form: form to be tested
	test_case: dict containing tuple of field value and expected error messages (list)
	"""
	# generate test_form values to populate form for testing
	test_args = {}
	test_errors = {}
	for key in test_case:
		test_args[key] = test_case[key][0]
		if test_case[key][1] is not None:
			test_errors[key] = test_case[key][1]
	test_args = ImmutableMultiDict(test_args)
	with test_app.app_context():
		form = test_form(formdata=test_args)
		# if no validation errors to check form, check that form validates
		if len(test_errors) == 0:
			assert form.validate()
		# otherwise check that it doesn't validate and correct value errors are included
		else:
			assert not form.validate()
			for key in test_errors:
				assert key in form.errors
				assert test_errors[key] in form.errors[key]


@pytest.mark.usefixtures("activeClient")
class TestGroupMemberApprove(FormTest):

	formType = GroupMemberApproveForm

	def make_form(self, formDict):
		"""Override FormTest make form to populate choices"""
		super().make_form(formDict)
		self.form.populate_choices(current_user)
	
	def test_new(self, testGroupRequest):
		testCase = {"request": testGroupRequest.id}
		self.new(testCase)
		
	def test_missingRequired(self, testGroupRequest):
		testCase = {}
		key = 'request'
		errorMsg = "Please select at least one name to approve."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)

	def test_invalidRequest(self, testGroupRequest):
		testCase = {"request": testGroupRequest.id + 1}
		key = 'request'
		errorMsg = "Invalid request. Please select request from the list."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)
	
	def test_notGroupAdmin(self, testGroupRequest2):
		testCase = {"request": testGroupRequest2.id}
		key = 'request'
		errorMsg = "User not authorized to approve this request."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)
	
	def test_populate_choices(self, testGroupRequest):
		self.form = self.formType()
		self.form.populate_choices(current_user)
		r = testGroupRequest
		assert self.form.request.choices == [(1, f"{r.group.name} - {r.requestor.full_name}")]		
	
	



@pytest.mark.usefixtures("activeClient")
class TestGroupDelete(FormTest):

	formType = GroupDeleteForm

	def make_form(self, formDict):
		super().make_form(formDict)
		self.form.populate_choices(current_user)

	def test_new(self, testGroup):
		testCase = {"name": testGroup.id}
		self.new(testCase)
	
	def test_missingRequired(self):
		testCase = {}
		key = 'name'
		errorMsg = "At least one group must be selected."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)
	
	def test_notOnGroupList(self, testGroup2):
		testCase = {"name": testGroup2.id}
		key = 'name'
		errorMsg = "Please select a group from the list."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)

	def test_groupDoesNotExist(self, testGroup2):
		testCase = {"name": 100}
		key = 'name'
		errorMsg = "Please select a group from the list."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)	

	def test_populateChoices(self):
		self.form = self.formType()
		self.form.populate_choices(current_user)
		assert self.form.name.choices == [(1, 'Qhiv Hoa')]

@pytest.mark.usefixtures("activeClient")
class TestFriendDelete(FormTest):

	formType = FriendDeleteForm

	def make_form(self, formDict):
		"""Helper method to generate Provider form for tests."""
		super().make_form(formDict)
		self.form.populate_choices(current_user)

	def test_new(self, testUser2):
		testCase = {"name": testUser2.id}
		self.new(testCase)
	
	def test_missingRequired(self):
		testCase = {}
		key = 'name'
		errorMsg = "At least one name must be selected."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)
	
	def test_notFriend(self, testUser3):
		testCase = {"name": testUser3.id}
		key = 'name'
		errorMsg = "Please select friend from list."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)		

	def test_populateChoices(self):
		self.form = self.formType()
		self.form.populate_choices(current_user)
		assert self.form.name.choices == [(1, 'Sarah Smith')]

@pytest.mark.usefixtures("activeClient")
class TestFriendApprove(FormTest):

	formType = FriendApproveForm

	def make_form(self, formDict):
		"""Override FormTest make form to populate choices"""
		super().make_form(formDict)
		self.form.populate_choices(current_user)
	
	def test_new(self, testFriendrequest):
		testCase = {"name": [testFriendrequest.id]}
		self.new(testCase)
	
	def test_newMultiple(self, testFriendrequest, testFriendrequest2):
		testCase = {"name":[testFriendrequest.id, testFriendrequest2.id]}
		self.new(testCase)
		
	def test_missingRequired(self, testFriendrequest):
		testCase = {}
		key = 'name'
		errorMsg = "Please select at least one name to approve."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)

	def test_invalidName(self, testFriendrequest):
		testCase = {"name": testFriendrequest.id + 1}
		key = 'name'
		errorMsg = "Please select name from the list."
		self.make_form(testCase)
		self.assertNot(key, errorMsg)	
	

class TestGroupCreate(FormTest):

	formType = GroupCreateForm

	def test_new(self, baseGroupNew):
		self.new(baseGroupNew)
	
	@pytest.mark.parametrize('key, errorMsg', [
		('name', 'Group name is required.'),
		('description', 'Description is required.')
	])
	def test_missingRequired(self, baseGroupNew, key, errorMsg):
		self.missingRequired(baseGroupNew, key, errorMsg)

	def test_duplicateName(self, baseGroupNew):
		key = 'name'
		errorMsg = 'Name is already registered.'
		baseGroupNew[key] = "Shannon's Bees"
		self.make_form(baseGroupNew)
		self.assertNot(key, errorMsg)


@pytest.mark.usefixtures("activeClient")
class TestFriendSearch(FormTest):
    
    formType = FriendSearchForm
    
    def test_new(self, baseFriendSearch):
        self.new(baseFriendSearch)

    @pytest.mark.parametrize("key, errorMsg", [
            ('id', "Name is required."),
            ('name', 'Name is required.')
    ])    
    def test_missingRequired(self, baseFriendSearch, key, errorMsg):
        self.missingRequired(baseFriendSearch, key, errorMsg)
    
    def test_alreadyFriends(self):
        search = {'id': 1, 'name': "Sarah Smith"}
        key = 'id'
        errorMsg = 'You are already friends with this person.'
        self.make_form(search)
        self.assertNot(key, errorMsg)
    
    def test_oneself(self):
        search = {'id': current_user.id, 'name': current_user.full_name}
        key = 'id'
        errorMsg = 'You are naturally friends with yourself.  No need to add to friend network.'        
        self.make_form(search)
        self.assertNot(key, errorMsg)

    def test_personDoesNotExist(self):
        search = {'id': 1000, 'name': "Abraham Lincoln"}
        key = 'id'
        errorMsg = 'Person does not exist, please choose a different person to add.'
        self.make_form(search)
        self.assertNot(key, errorMsg)

@pytest.mark.usefixtures("activeClient")
class TestGroupSearch(FormTest):
	
    formType = GroupSearchForm
    
    def test_new(self, baseGroupSearch):
        self.new(baseGroupSearch)
        
    @pytest.mark.parametrize("key, errorMsg", [
        ('name', 'Group name is required.')
    ])
    def test_missingRequired(self, baseGroupSearch, key, errorMsg):
        self.missingRequired(baseGroupSearch, key, errorMsg)



class TestGroupEdit(FormTest):

	formType = GroupEditForm
	
	def test_new(self, baseGroup):
		self.new(baseGroup)
	
	@pytest.mark.parametrize('key, errorMsg',[
		('name', 'Group name is required.'),
		('description', 'Description is required.'),
		('id', 'Group ID is required.  Please do not remove.')
	])
	def test_missingRequired(self, baseGroup, key, errorMsg):
		self.missingRequired(baseGroup, key, errorMsg)
	
	def test_idDoesNotExist(self, baseGroup):
		key = 'id'
		baseGroup[key] = 8
		errorMsg = "Invalid update. Group does not exist. Refresh and try again."
		self.make_form(baseGroup)
		self.assertNot(key, errorMsg)
	
	def test_duplicateGroupName(self, baseGroup):
		key = 'name'
		baseGroup[key] = "Shawshank Redemption Fans"
		errorMsg = "Group name is already registered."
		self.make_form(baseGroup)
		self.assertNot(key, errorMsg)		
	

class TestAddress(FormTest):
	"""Test address field."""

	formType = AddressField

	def test_new(self, baseAddress):
		self.new(baseAddress)

	@pytest.mark.parametrize('key, errorMsg', [
		('line1', 'Street address is required.'),
		('city', 'City is required.'),
		('state', 'State is required.'),
		('zip', 'Zip code is required.')
	])		
	def test_missingRequired(self, baseAddress, key, errorMsg):
		self.missingRequired(baseAddress, key, errorMsg)
	
	def test_zipTooShort(self, baseAddress):
		baseAddress['zip'] = "282"
		self.make_form(baseAddress)
		errorMsg = "Please enter a 5 digit zip code."
		self.assertNot('zip', errorMsg)

	def test_zipWithLetters(self, baseAddress):
		baseAddress['zip'] = "2821a"
		self.make_form(baseAddress)
		errorMsg = "Only include numbers in zip code."
		self.assertNot('zip', errorMsg)
	

class TestLogin(FormTest):
	"""Test user login form."""

	formType = LoginForm

	def test_new(self, baseLogin):
		self.new(baseLogin)
	
	@pytest.mark.parametrize('key, errorMsg', [
		('username', 'Username is required.'),
		('password', 'Password is required.'),
	])		
	def test_missingRequired(self, baseLogin, key, errorMsg):
		self.missingRequired(baseLogin, key, errorMsg)

class TestRegister(FormTest):
	"""Tests for User Registration form."""

	formType = RegistrationForm

	def test_new(self, baseUserNew):
		self.new(baseUserNew)
	
	@pytest.mark.parametrize('key, errorMsg', [
		('first_name', 'First name is required.'),
		('last_name', 'Last name is required.'),
		('email', 'Email address is required.'),
		('username', 'Username is required.'),
		('password', 'Password is required.'),
		('confirmation', 'Password confirmation is required.')
	])
	def test_missingRequired(self, baseUserNew, key, errorMsg):
		self.missingRequired(baseUserNew, key, errorMsg)

	def test_duplicateEmail(self, baseUserNew):
		baseUserNew['email'] = "sarahsmith@yahoo.com"
		errorMsg = 'Email address is already registered.'
		self.make_form(baseUserNew)
		self.assertNot('email', errorMsg)
	
	def test_duplicateUsername(self, baseUserNew):
		baseUserNew['username'] = "sarahsmith"
		errorMsg = 'Username is already registered.'
		self.make_form(baseUserNew)
		self.assertNot('username', errorMsg)
	
	def test_invalidEmail(self, baseUserNew):
		baseUserNew['email'] = "invalidemailyahoo.com"
		errorMsg = 'Invalid email address.'
		self.make_form(baseUserNew)
		self.assertNot('email', errorMsg)

	def test_passwordTooShort(self, baseUserNew):
		baseUserNew['password'] = 'short'
		errorMsg = 'Field must be between 7 and 15 characters long.'
		self.make_form(baseUserNew)
		self.assertNot('password', errorMsg)

	def test_passwordTooLong(self, baseUserNew):
		baseUserNew['password'] = 'nottooshortbutwaywaytoolong'
		errorMsg = 'Field must be between 7 and 15 characters long.'
		self.make_form(baseUserNew)
		self.assertNot('password', errorMsg)

	def test_invalidEmail(self, baseUserNew):
		baseUserNew['email'] = "invalidemailyahoo.com"
		errorMsg = 'Invalid email address.'
		self.make_form(baseUserNew)
		self.assertNot('email', errorMsg)
	
	def test_passwordConfirmationMismatch(self, baseUserNew):
		baseUserNew['confirmation'] = "different"
		errorMsg = 'Passwords must match.'
		self.make_form(baseUserNew)
		self.assertNot('confirmation', errorMsg)		

@pytest.mark.usefixtures("activeClient")
class TestPasswordUpdate(FormTest):
	"""Test user password update form."""

	formType = PasswordChangeForm

	def test_new(self, basePwUpdate):
		self.new(basePwUpdate)
	
	@pytest.mark.parametrize('key, errorMsg', [
		('old', "Please enter old password."),
		('new', "Please choose a new password."),
		('confirmation', "Please confirm new password.")
	])
	def test_missingRequired(self, basePwUpdate, key, errorMsg):
		self.missingRequired(basePwUpdate, key, errorMsg)

	def test_invalidOld(self, basePwUpdate):
		basePwUpdate['old'] = "WrongPassword"
		self.make_form(basePwUpdate)
		errorMsg = "Invalid password, please try again."
		self.assertNot('old', errorMsg)

	def test_invalidConfirmation(self, basePwUpdate):
		basePwUpdate['confirmation'] = "differentPassword"
		self.make_form(basePwUpdate)
		errorMsg = "Passwords must match."
		self.assertNot('confirmation', errorMsg)

	def test_duplicateNew(self, basePwUpdate):
		basePwUpdate['new'] = "password"
		self.make_form(basePwUpdate)
		errorMsg = "New password is same as old password.  Please choose a different password."
		self.assertNot('new', errorMsg)		

@pytest.mark.usefixtures("activeClient")
class TestUserUpdate(FormTest):
	"""Test user update form."""

	formType = UserUpdateForm

	def test_new(self, baseUser):
		self.new(baseUser)
	
	@pytest.mark.parametrize("key, errorMsg", [
		('first_name', 'First name is required.'),
		('last_name', 'Last name is required.'),
		('email', 'Email address is required.'),
		('username', 'Username is required.')
	])
	def test_missingrequire(self, baseUser, key, errorMsg):
		self.missingRequired(baseUser, key, errorMsg)

	def test_duplicateEmail(self, baseUser):
		baseUser['email'] = "sarahsmith@yahoo.com"
		errorMsg = 'Email address is already registered, please choose a different email address.'
		self.make_form(baseUser)
		self.assertNot('email', errorMsg)
	
	def test_duplicateUsername(self, baseUser):
		baseUser['username'] = "sarahsmith"
		errorMsg = 'Username is already registered, please choose a different username.'
		self.make_form(baseUser)
		self.assertNot('username', errorMsg)
	
	def test_invalidEmail(self, baseUser):
		baseUser['email'] = "invalidemailyahoo.com"
		errorMsg = 'Invalid email address.'
		self.make_form(baseUser)
		self.assertNot('email', errorMsg)		

class TestReview(FormTest):
	"""Test review form validation."""

	formType = ReviewForm

	def make_form(self, formDict):
		super().make_form(formDict)
		try:
			biz = Provider.query.get(formDict['id'])
			categories = biz.categories
		except KeyError:
			categories = Category.query.all()
		catList = [(c.id, c.name) for c in categories]
		self.form.category.choices = catList

	def test_new(self, baseReview):
		self.new(baseReview)

	@pytest.mark.parametrize('key, errorMsg', [
		('name', 'Business name is required.'),
		('id', "Business id is required. Do not remove from form submission."),
		('category', 'Category is required.'),
		('rating', 'Rating is required.'),
		('cost', 'Cost is required.')])
	def test_missingRequired(self, baseReview, key, errorMsg):
		self.missingRequired(baseReview, key, errorMsg)
	
	def test_idNameMismatch(self, baseReview):
		baseReview['id'] = 3
		self.make_form(baseReview)
		errorMsg = "Submitted name and id combination are invalid."
		self.assertNot('name', errorMsg)
	
	def test_invalidCategory(self, baseReview):
		baseReview['category'] = 2
		self.make_form(baseReview)
		errorMsg = "Category not valid for business being reviewed."
		self.assertNot('category', errorMsg)

	def test_invalidRating(self, baseReview):
		baseReview['rating'] = 7
		self.make_form(baseReview)
		errorMsg = "Not a valid choice"
		self.assertNot('rating', errorMsg)
	
	def test_invalidCost(self, baseReview):
		baseReview['cost'] = 7
		self.make_form(baseReview)
		errorMsg = "Not a valid choice"
		self.assertNot('cost', errorMsg)

class TestProviderAdd(FormTest):
	"""Test Provider add form."""

	formType = ProviderAddForm
	
	def make_form(self, formDict):
		super().make_form(formDict)
		self.form.category.choices = Category.list(self.formDict.get('sector'))

	def test_new(self, baseProviderNew):
		self.new(baseProviderNew)

	@pytest.mark.parametrize('key, errorMsg', [('name', 'Business name is required.'),
									('sector', 'Sector is required.'),
									('category', 'Category is required.'),
									('telephone', 'Telephone number is required.')
									])	
	def test_missingRequired(self, baseProviderNew, key, errorMsg):
		super().missingRequired(baseProviderNew, key, errorMsg)
	
	def test_duplicateEmail(self, baseProviderNew):
		baseProviderNew['email'] = 'douthit@gmail.com'
		key = 'email'
		errorMsg = 'Email address is already registered.'
		self.make_form(baseProviderNew)
		self.assertNot(key, errorMsg)
	
	def test_invalidEmail(self, baseProviderNew):
		baseProviderNew['email'] = 'douthitgmail.com'
		key = 'email'
		errorMsg = 'Invalid email address.'
		self.make_form(baseProviderNew)
		self.assertNot(key, errorMsg)

	def test_duplicateTelephone(self, baseProviderNew):
		baseProviderNew['telephone'] = '704-843-1910'
		key = 'telephone'
		errorMsg = 'Telephone number is already registered.'
		self.make_form(baseProviderNew)
		self.assertNot(key, errorMsg)	

	def test_duplicateBusiness(self):
		p = Provider.query.get(2)
		key = 'name'
		errorMsg = "Business already exists, please look up business or use a "\
			"different name/address."
		cats = [c.name for c in p.categories]
		test_case = {"sector": 1, "category": cats, "name": p.name,
					"telephone": p.telephone, "email": p.email,
					"address-line1": p.address.line1,
					"address-city": p.address.city,
					"address-state": p.address.state.id,
					"address-zip": p.address.zip}
		self.make_form(test_case)
		self.assertNot(key, errorMsg)
	
	def test_unknown(self, baseProviderNew):
		baseProviderNew.update({"address-line1": "", "address-zip": "",
		    "address-unknown": "True"})
		self.make_form(baseProviderNew)
		assert self.form.validate()

class TestProviderAddress(FormTest):

	formType = ProviderAddress

	def test_new(self):
		a = {"line1": "7708 Covey Chase Dr", "city": "Charlotte", "state": 1,
                 "zip": "28210", "unknown": "False"}
		self.make_form(a)
		assert self.form.validate()

	def test_unknown(self):
		a = {"line1": None, "city": "Charlotte", "state": 1,
                 "zip": None, "unknown": "True"}
		self.make_form(a)
		assert self.form.validate()


@pytest.mark.usefixtures("test_app", "dbSession", "activeClient")
class TestProviderSearch(object):
	"""Test provider search form."""
	def test_new(self, baseProviderSearch, activeClient):
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		form.validate()
		assert form.validate()

	def test_newGPS(self, baseProviderSearch):
		baseProviderSearch.update({"location": "gps", "gpsLat": 42.00,
								"gpsLong": -81.000})
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		assert form.validate()

	def test_newGPSInvalid(self, baseProviderSearch):
		baseProviderSearch.update({"location": "gps", "gpsLat": "not_lat",
								"gpsLong": "not_long"})
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		assert not form.validate()
		msg = "GPS location data must be numeric type."
		assert msg in form.errors['gpsLat']

	def test_newGPSNoLatLong(self, baseProviderSearch):
		baseProviderSearch.update({"location": "gps"})
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		form.validate()
		assert not form.validate()
		msg = 'Must allow access to device location if gps selected as location source.'
		assert msg in form.errors['gpsLat']

	def test_newManual(self, baseProviderSearch):
		baseProviderSearch.update({"location": "manual",
								"manual_location": "7708 Covey Chase Dr, Charlotte NC 28210"})
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		assert form.validate()		

	def test_populateChoices(self, baseProviderSearch):
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		assert form.category.choices == [(1, 'Electrician'), (2, 'Plumber')]
		assert form.location.choices[0] == ("home", 
										"Home - 7708 Covey Chase Dr, Charlotte, NC")
		assert form.location.choices[1] == ("gps", "New - Use GPS")
		assert form.location.choices[2] == ("manual", "New - Manually Enter")									 
		assert len(form.location.choices) == 3

	def test_populateChoicesLocationSession(self, baseProviderSearch, mockGeoResponse):
		searchLocation = Location("manual", "8012 Covey Chase Dr, Charlotte, NC",
								("", ""))
		baseProviderSearch['location'] = "manualExisting"
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		assert form.location.choices[0] == ("manualExisting", "8012 Covey Chase Dr, Charlotte, NC")

	def test_initialize(self, baseProviderSearch, mockGeoResponse):
		searchLocation = Location("manual", "8012 Covey Chase Dr, Charlotte, NC",
								("", ""))
		baseProviderSearch.update({
			"location": "manual",
			"manual_location": "8012 Covey Chase Dr, Charlotte, NC"
		})
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.initialize()
		assert form.location.choices[0] == ("manualExisting", "8012 Covey Chase Dr, Charlotte, NC")	
		assert form.manual_location.data == ""

	@pytest.mark.parametrize('key, errorMsg', [('location', 'Search location is required.'),
									('sector', 'Sector is required.'),
									('category', 'Category is required.'),
									('sort', 'Sort criteria is required.')
									])
	def test_newMissingRequired(self, baseProviderSearch, key, errorMsg):
		baseProviderSearch.pop(key)
		formdata = ImmutableMultiDict(baseProviderSearch)
		form = ProviderSearchForm(formdata=formdata)
		form.populate_choices()
		form.validate()
		assert errorMsg in form.errors[key]

class TestPasswordReset(FormTest):
	"""Test password reset form."""

	formType = PasswordResetForm

	def test_new(self, basePasswordReset):
		self.new(basePasswordReset)
	
	@pytest.mark.parametrize('key, errorMsg', [
		('password_new', 'Please choose a new password.'),
		('password_confirmation', 'Please confirm new password.')
	])
	def test_missingRequired(self, basePasswordReset, key, errorMsg):
		self.missingRequired(basePasswordReset, key, errorMsg)
	
	def test_badConfirmation(self, basePasswordReset):
		key = 'password_confirmation'
		basePasswordReset[key] = 'password3'
		errorMsg = 'Passwords must match.'
		self.make_form(basePasswordReset)
		self.assertNot(key, errorMsg)

class TestPasswordResetRequest(FormTest):
	"""Test password reset request form."""

	formType = PasswordResetRequestForm

	def test_new(self):
		testCase = {"email" :"test@test.com"}
		self.new(testCase)
	
	def test_missingRequired(self):
		testCase = {"email" :"test@test.com"}
		key = 'email'
		errorMsg = 'Email address is required.'
		self.missingRequired(testCase, key, errorMsg)

	def test_badEmail(self):
		testCase = {"email" :"invalidemailyahoo.com"}
		key = 'email'
		errorMsg = 'Invalid email address.'
		self.make_form(testCase)
		self.assertNot(key, errorMsg)

