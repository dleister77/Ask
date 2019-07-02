from flask import current_app, has_request_context, _request_ctx_stack
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField,
                     SubmitField, FormField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                Optional, ValidationError)
                                
from app.models import State, User


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
    line1 = StringField("Street Address", validators=[DataRequired(message="Street address is required.")])
    line2 = StringField("Address Line 2", validators=[Optional()])
    city = StringField("City", validators=[DataRequired(message="City is required.")])
    state = SelectField("State", choices=State.list(), coerce=int,
                         validators=[DataRequired(message="State is required.")])
    zip = StringField("Zip", validators=[DataRequired(message="Zip code is required.")])

    def validate_zip(form, field):
        if len(field.data) != 5:
            raise ValidationError('Please enter a 5 digit zip code.')
        elif not field.data.isdigit():
            raise ValidationError('Only include numbers in zip code.')

class LoginForm(FlaskForm):
    """Defines user login form."""
    username = StringField("Username", validators=[DataRequired(message="Username is required.")])
    password = PasswordField("Password", validators=[DataRequired(message="Password is required.")])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(message="First name is required.")])
    last_name = StringField("Last Name", validators=[DataRequired(message = "Last name is required.")])
    address = FormField(AddressField) 
    email = StringField("Email Address", validators=[DataRequired(message="Email address is required."), Email(), 
                         unique_check(User, User.email)])
    username = StringField("Username", validators=[DataRequired(message="Username is required.")])
    password = PasswordField("Password", validators=[DataRequired(message="Password is required."), 
            Length(min=7, max=15)])
    confirmation = PasswordField("Confirm Password",
                validators=[DataRequired(message="Password confirmation is required."),  
                EqualTo('password', message="Passwords must match.")])
    submit = SubmitField("Submit")
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is already registered, please choose a "
                                  "different name.")

class UserUpdateForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(message="First name is required.")])
    last_name = StringField("Last Name", validators=[DataRequired(message = "Last name is required.")])
    address = FormField(AddressField) 
    email = StringField("Email Address", validators=[DataRequired(message="Email address is required."), Email()])
    username = StringField("Username", validators=[DataRequired(message="Username is required.")])
    submit = SubmitField("Submit")
    
    def validate_username(self, username):
        print(f"auth form request status: {has_request_context()}")
        print(f"auth form request stack: {_request_ctx_stack.top}")
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
    old = PasswordField("Old Password", validators=[DataRequired(message="Please enter old password.")])
    new = PasswordField("New Password", validators=[DataRequired(message="Please choose a new password."), 
            Length(min=7, max=15)])
    confirmation = PasswordField("Confirm New Password",
                                 validators=[DataRequired(message="Please confirm new password."), 
                                 EqualTo('new', 
                                 message="Passwords must match.")])
    submit = SubmitField("Submit")

    def validate_old(self, old):
        if not current_user.check_password(old.data):
            raise ValidationError("Invalid password, please try again.")
    
    def validate_new(self, new):
        if current_user.check_password(new.data):
            raise ValidationError("New password is same as old password.  Please choose a different password.")

class PasswordResetRequestForm(FlaskForm):
    """Form to request password reset via email."""
    email = StringField("Email", validators=[DataRequired(message="Email address is required."), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    """Form to reset password via email link."""
    password_new = PasswordField("New Password", validators=[DataRequired(message="Please choose a new password."), 
            Length(min=7, max=15)])
    password_confirmation = PasswordField("Confirm New Password",
                            validators=[DataRequired(message="Please confirm new password."), 
                            EqualTo('password_new', 
                            message="Passwords must match.")])
    submit = SubmitField("Submit")