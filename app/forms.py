from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, \
     SubmitField, FormField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import State, User

def state_list():
    """Query db to populate state list on forms."""
    return [(s.state, s.state) for s in State.query.order_by("state")]

class AddressForm(FlaskForm):
    line1 = StringField("Street Address", validators=[DataRequired()])
    line2 = StringField("Street Address Cont'd")
    city = StringField("City", validators=[DataRequired()])
    state = SelectField("State", choices=state_list(), validators=[DataRequired()])
    zip = StringField("State", validators=[DataRequired()])

class LoginForm(FlaskForm):
    """Defines user login form."""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(AddressForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
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
            raise ValidationError("Username already exists, please choose a "
                                  "different name.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email address already registered. Please "
                                  "choose a different email address.")

