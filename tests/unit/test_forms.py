import pytest
from app import create_app
from app.relationship.forms import (GroupCreateForm, FriendSearchForm, GroupSearchForm)
import os
from tests.conftest import login, logout, TestConfig
from werkzeug.datastructures import FileStorage

app = create_app(TestConfig)
with app.app_context():
	from app.main.forms import ProviderAddForm, ProviderSearchForm, ReviewForm
	from app.auth.forms import UserUpdateForm, PasswordChangeForm, RegistrationForm, LoginForm, AddressField

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
	with test_app.app_context():
		form = test_form(**test_args)
		# if no validation errors to check form, check that form validates
		if len(test_errors) == 0:
			form.validate()
			assert form.validate()
		# otherwise check that it doesn't validate and correct value errors are included
		else:
			assert not form.validate()
			for key in test_errors:
				assert key in form.errors
				assert test_errors[key] in form.errors.values()

def scenarioUpdate(test_case, parameters, values, assertions):
	""""Update test_case for update scenario
	test_case: base test case
	parameters: parameter(dict key) to be updated.  single value or list.
	values: updated values parameter values.  single value or list of values if
	 		multiple parameters being updated.
	assertions: list of assertions to be updated. single list or list of lists.
	"""
	if parameters == None:
		pass
	elif type(parameters) == list:
		for param, val, assertion in zip(parameters, values, assertions):
			test_case[param] = (val, assertion)
	else:
		test_case[parameters] = (values, assertions)


@pytest.mark.parametrize("description", [("soccer team", None),
                                         ("", ["Description is required."])])
@pytest.mark.parametrize("name", [("Liverpool FC", None),
                                  ("Shannon's Bees", ["Name is already registered."]),
								  ("", ["Group name is required."])])
def test_group_create(test_app, active_client, test_db, name, description):
	test_case = {"name": name, "description": description}
	form_test(test_app, GroupCreateForm, test_case)


@pytest.mark.parametrize("name", [("Mark Johnson", None),
								  ("", ["Name is required."])])
@pytest.mark.parametrize("value", [(3, None), ("", ["Name is required."]),
								   (1, ["You are already friends with this person."]), 
								   (2, ["You are naturally friends with yourself.  No need to add to friend network."])])							  
def test_friend_search(test_app, active_client, test_db, name, value):
	test_case = {"name": name, "value": value}
	form_test(test_app, FriendSearchForm, test_case)


@pytest.mark.parametrize("name", [("Qhiv Hoa", None),
								  ("", ["Group name is required."])])
@pytest.mark.parametrize("value", [(2, None), ("", ["Group name is required."]),
								   (1, ["You are already a member of this group."]), 
								   (5, ["Group does not exist, please choose a different group to add."])])							  
def test_group_search(test_app, active_client, test_db, name, value):
	test_case = {"name": name, "value": value}
	form_test(test_app, GroupSearchForm, test_case)


@pytest.mark.parametrize("parameters, values, assertions", [
						(None, None, None),
						("line1", "", ["Street address is required."]),
						("line2", "", None),
						("city", "", ["City is required."]),
						("state", "", ["State is required."]),
						("state", "5", ["Not a valid choice"]),
						("zip", "282", ["Please enter a 5 digit zip code."]),
						("zip", "2821a", ["Only include numbers in zip code."])
						])
def test_address_field(test_app, active_client, test_db, base_address,
						parameters, values,	assertions):
	test_case = base_address
	for key, base_value in test_case.items():
		test_case[key] = (base_value, None)
	scenarioUpdate(test_case, parameters, values, assertions)
	form_test(test_app, AddressField, test_case)
	
@pytest.mark.parametrize("parameters, values, assertions",[
						(None, None, None),
						("password", "", ["Password is required."]),
						("username", "", ["Username is required."])
						])
def test_login_form_2(test_app, test_client, test_db, base_login, parameters,
					  values, assertions):
	test_case = base_login
	for key, base_value in test_case.items():
		test_case[key] = (base_value, None)
	scenarioUpdate(test_case, parameters, values, assertions)
	form_test(test_app, LoginForm, test_case)

@pytest.mark.parametrize("parameters, values, assertions", [
						(None, None, None),
						("first_name", "", ["First name is required."]),
						("last_name", "", ["Last name is required."]),
						("email", "", ["Email address is required."]),
						("email", "sarahsmith@yahoo.com", ["Email address is already registered."]),
						("email", "rfirminolfc", ["Invalid email address."]),
						("username", "", ["Username is required."]),
						("username", "yardsmith", ["Username is already registered, please choose a different name."]),
						("password", "", ["Password is required."]),
						("password", "123456", ["Field must be between 7 and 15 characters long."]),
						("password", "passwordpassword50", ["Field must be between 7 and 15 characters long."]),
						("confirmation", "", ["Password confirmation is required."]),
						("confirmation", "incorrectpw", ["Passwords must match."])
						])
def test_registration_form(test_app, active_client, test_db, base_user_new, 
						  parameters, values, assertions):
	test_case = base_user_new
	for key, base_value in test_case.items():
		test_case[key] = (base_value, None)
	scenarioUpdate(test_case, parameters, values, assertions)
	form_test(test_app, RegistrationForm, test_case)

@pytest.mark.parametrize("parameters, values, assertions", [
						(None, None, None),
						("old", "", ["Please enter old password."]),
						("old", "incorrect", ["Invalid password, please try "
											  "again."]),
						("new", "", ["Please choose a new password."]),
						("new", "password", ["New password is same as old password.  Please choose a different password."]),
						("confirmation", "", ["Please confirm new password."]),
						("confirmation", "different", ["Passwords must match."])
						])
def test_password_update(test_app, active_client, test_db, base_pw_update, 
						  parameters, values, assertions):
	test_case = base_pw_update
	for key, base_value in test_case.items():
		test_case[key] = (base_value, None)
	scenarioUpdate(test_case, parameters, values, assertions)
	form_test(test_app, PasswordChangeForm, test_case)


@pytest.mark.parametrize("parameters, values, assertions",[
						(None, None, None),
						("first_name", "", ["First name is required."]),
						("last_name", "", ["Last name is required."]),
						("email", "", ["Email address is required."]),
						("email", "sarahsmith@yahoo.com",
						 ["Email address is already registered, please choose a "
                                  "different email address."]),
						("email", "invalidemail.com", ["Invalid email address."]),
						("username", "", ["Username is required."]),
						("username", "sarahsmith", ["Username is already registered, "
										 "please choose a different username."])
						])					
def test_user_update(test_app, active_client, test_db, base_user, parameters, values, assertions):
	test_case = base_user
	for key, base_value in test_case.items():
		test_case[key] = (base_value, None)
	scenarioUpdate(test_case, parameters, values, assertions)
	form_test(test_app, UserUpdateForm, test_case)


@pytest.mark.parametrize("parameters, values, assertions", [
						 ("category", "", ["Category is required."]),
						 ("category", "5", ["Not a valid choice"]),
						 ("name", "", ["Provider name is required."]),
						 ("name", "5", ["Please choose a provider from the list."]),
						 ("rating", "", ["Rating is required."]),
						 ("rating", "7", ["Not a valid choice"]),
						 ("service_description", "", None),
						 ("service_date", "", None),
						 ("comments", "", None),
						 (["category", "name", "rating", "service_description"],
						 ["", "", "", ""], [["Category is required."], 
						 ["Provider name is required."], ["Rating is required."],
						 None])
						 ])
def test_review(test_app, test_db, base_review, parameters, values, assertions):
	for key, base_value in base_review.items():
		base_review[key] = (base_value, None)
	test_case = base_review
	form_test(test_app, ReviewForm, test_case)
	scenarioUpdate(test_case, parameters, values, assertions)
	form_test(test_app, ReviewForm, test_case)

@pytest.mark.parametrize("parameters, values, assertions", [
						(None, None, None),
						("name", "", ["Provider name is required."]),
						("category", "", ["Category is required."]),
						("telephone", "", ["Telephone number is required."]),
						("telephone", "704-843-1910", ["Telephone number is already registered."]),
						("email", "douthit@gmail.com", ["Email address is already registered."]),
						("email", "douthitgmail.com", ["Invalid email address."]),
						(["name", "address"], 
						 ["Evers Electric", {"line1": "3924 Cassidy Drive",
						 					"line2": "", "city": "Waxhaw", 
											 "state": 1, "zip": "28173"}
						 ],
						 [["Provider already exists, please select a new name."],
						  None])
])
def test_provider_add(test_app, test_db, base_provider_new, parameters, values, assertions):
	test_case = base_provider_new
	for key, base_value in test_case.items():
		test_case[key] = (base_value, None)
	scenarioUpdate(test_case, parameters, values, assertions)
	form_test(test_app, ProviderAddForm, test_case)


@pytest.mark.parametrize("category", [("1", None),
									  ("", ["Category is required."])])
@pytest.mark.parametrize("city", [("Charlotte", None),
								  ("", ["City is required."])])
@pytest.mark.parametrize("state", [("1", None), ("", ["State is required."]),
								   ("5", ["Not a valid choice"])])
@pytest.mark.parametrize("friends_only", [(True, None)])
@pytest.mark.parametrize("groups_only", [(True, None)])				  
def test_provider_search(test_app, test_db, category, city, state,
						 friends_only, groups_only):
	if friends_only[0] == True and groups_only[0] == True:
		friends_only = (True, ["Friends Only and Groups Only are not allowed to both be selected."])
		groups_only = (True, ["Groups Only and Friends Only are not allowed to both be selected."])
	test_case = {"category": category, "city": city, "state": state,
				 "friends_only": friends_only, "groups_only": groups_only}
	form_test(test_app, ProviderSearchForm, test_case)





