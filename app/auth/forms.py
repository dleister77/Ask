from flask import current_app, has_request_context, _request_ctx_stack
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField,
                     SubmitField, FormField)
from wtforms.validators import (InputRequired, Email, EqualTo, Length,
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
    """Form to capture user or business address.

    Fields:
       line1 (str): street address line 1 (i.e. 100 Main St)
       line2 (str): optional, 2nd line of street address (i.e. apt 3b)
       city (str): address city
       state (select): address state
       zip (str): 5 digit zip code
    
    Methods:
       validate_zip: check zip code, verifies 5 digits and only numbers in zip code
    """
    line1 = StringField("Street Address", validators=[InputRequired(message="Street address is required.")])
    line2 = StringField("Address Line 2", validators=[Optional()])
    city = StringField("City", validators=[InputRequired(message="City is required.")])
    state = SelectField("State", choices=State.list(), coerce=int,
                         validators=[InputRequired(message="State is required.")])
    zip = StringField("Zip", validators=[InputRequired(message="Zip code is required.")])

    def validate_zip(form, field):
        if len(field.data) != 5:
            raise ValidationError('Please enter a 5 digit zip code.')
        elif not field.data.isdigit():
            raise ValidationError('Only include numbers in zip code.')

class LoginForm(FlaskForm):
    """Defines user login form.
    
    Fields:
        username (str): User username
        password (password): User password
        remember_me (boolean): sets session to remember user after they close
            browser
    """
    username = StringField("Username", validators=[InputRequired(message="Username is required.")])
    password = PasswordField("Password", validators=[InputRequired(message="Password is required.")])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    """Collects information to register new user for site.

    Fields:
        first_name (str): User first name
        last_name (str): User last name
        address (FormField): AddressField (see above) for User
        email (str): Unique, user email address
        username (str): Unique, user username
        password (password): User password, 7 to 15 characters
        confirmation (password): confirmation of user password entered above
    """

    first_name = StringField("First Name", validators=[InputRequired(message="First name is required.")])
    last_name = StringField("Last Name", validators=[InputRequired(message = "Last name is required.")])
    address = FormField(AddressField) 
    email = StringField("Email Address", validators=[InputRequired(message="Email address is required."), Email(), 
                         unique_check(User, User.email)])
    username = StringField("Username", validators=[InputRequired(message="Username is required."),
                   unique_check(User, User.username)])
    password = PasswordField("Password", validators=[InputRequired(message="Password is required."), 
            Length(min=7, max=15)])
    confirmation = PasswordField("Confirm Password",
                validators=[InputRequired(message="Password confirmation is required."),  
                EqualTo('password', message="Passwords must match.")])
    submit = SubmitField("Submit")
    


class UserUpdateForm(FlaskForm):
    """Update user information.

    Fields:
        first_name (str): User first name
        last_name (str): User last name
        address (FormField): AddressField (see above) for User
        email (str): Unique, user email address
        username (str): Unique, user username
    
    Methods:
        validate_username: excluding current_user username, verifieds that 
            entered username does not belong to another user
        validate_email: exclude current user email address, verifies that 
            entered email address does not belong to another user
    """
    first_name = StringField("First Name", validators=[InputRequired(message="First name is required.")])
    last_name = StringField("Last Name", validators=[InputRequired(message = "Last name is required.")])
    address = FormField(AddressField) 
    email = StringField("Email Address", validators=[InputRequired(message="Email address is required."), Email()])
    username = StringField("Username", validators=[InputRequired(message="Username is required.")])
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
    """Form to change password.
    
    Fields:
        old (password): old password, to authenticate user prior to update
        new (password): new password, 7 to 15 characters
        confirmation (password): re-entry of new password to verify prio
            to update
    
    Methods:
        validate_old: checks that entered password is correct
        validate_new: checks that entered password is different from current
    """

    old = PasswordField("Old Password", validators=[InputRequired(message="Please enter old password.")])
    new = PasswordField("New Password", validators=[InputRequired(message="Please choose a new password."), 
            Length(min=7, max=15)])
    confirmation = PasswordField("Confirm New Password",
                                 validators=[InputRequired(message="Please confirm new password."), 
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
    """Form to request password reset via email.
    
    Fields:
        email (str): email address for password reset to be sent to
    """

    email = StringField("Email", validators=[
        InputRequired(message="Email address is required."),
        Email(message="Invalid email address.")])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    """Form to reset password via email link.
    
    Fields:
        password_new (password): new password on password reset
        password_confirmation (password): re-entry of password on reset

    """
    password_new = PasswordField("New Password", validators=[InputRequired(message="Please choose a new password."), 
            Length(min=7, max=15)])
    password_confirmation = PasswordField("Confirm New Password",
                            validators=[InputRequired(message="Please confirm new password."), 
                            EqualTo('password_new', 
                            message="Passwords must match.")])
    submit = SubmitField("Submit")

   