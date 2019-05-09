# from app import create_app
from app import db
from flask import current_app
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField,
                     SubmitField, FormField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)
from app.models import State, User, Category

def state_list():
    """Query db to populate state list on forms."""
    if current_app.config['TESTING'] == True:
        list = current_app.config['TEST_STATES']
    else:
        list = [(s.id, s.name) for s in State.query.order_by("name")]
    return list

def category_list():
    """Query db to populate state list on forms."""
    if current_app.config['TESTING'] == True:
        list = current_app.config['TEST_CATEGORIES']
    else:
        list = [(c.id, c.name) for c in Category.query.order_by("name")]
    return list

def unique_check(modelClass, columnName):
    """validate that no other entity in class registered for field.
    inputs:
        modelClass: db model class to query
        columnName: db column in modelclass.columname format
    """
    
    def _unique_check(form, field):
        key = {"email": "Email address",
               "telephone": "Telephone number",
               "name":"Name",
               "username": "Username"}
        message = f"{key[field.name]} is already registered."
        entity = modelClass.query.filter(columnName == field.data).first()
        if entity is not None:
            raise ValidationError(message)
    return _unique_check

def NotEqualTo(comparisonField):

    def _notEqualTo(form, field):
        compare_field = getattr(form, comparisonField)
        message = f"{field.label.text} and {compare_field.label.text} are not allowed to both be selected."
        if field.data is True and compare_field.data is True:
            raise ValidationError(message)
    return _notEqualTo

class AddressField(FlaskForm):
    line1 = StringField("Street Address", validators=[DataRequired()])
    line2 = StringField("Address Line 2")
    city = StringField("City", validators=[DataRequired()])
    state = SelectField("State", choices=state_list(), coerce=int,
                         validators=[DataRequired()])
    zip = StringField("Zip", validators=[DataRequired()])

    def validate_zip(form, field):
        if len(field.data) != 5:
            raise ValidationError('Please enter 5 digit zip code.')
        elif not field.data.isdigit():
            raise ValidationError('Only include numbers in zip code.')

class LoginForm(FlaskForm):
    """Defines user login form."""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    address = FormField(AddressField) 
    email = StringField("Email Address", validators=[DataRequired(), Email(), 
                         unique_check(User, User.email)])
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), 
            Length(min=7, max=15)])
    confirmation = PasswordField("Confirm Password",
                validators=[DataRequired(),  
                EqualTo('password', message="passwords must match")])
    submit = SubmitField("Submit")
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is already registered, please choose a "
                                  "different name.")

class UserUpdateForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    address = FormField(AddressField) 
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and user != current_user:
            raise ValidationError("Username is already registered, please choose a "
                                  "different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user != current_user:
            raise ValidationError("Email address is already registered, please choose a "
                                  "different email address.")

class PasswordChangeForm(FlaskForm):
    """Form to change password."""
    old = PasswordField("Old Password", validators=[DataRequired()])
    new = PasswordField("New Password", validators=[DataRequired(), 
            Length(min=7, max=15)])
    confirmation = PasswordField("Confirm New Password",
                                 validators=[DataRequired(), 
                                 EqualTo('new', 
                                 message="passwords must match")])
    submit = SubmitField("Submit")

    def validate_old(self, old):
        if not current_user.check_password(old.data):
            raise ValidationError("invalid password, try again.")
