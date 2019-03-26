from flask import request
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField,
     SubmitField, FormField, FieldList, DateField, FileField, TextAreaField,
     RadioField, SelectMultipleField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
 ValidationError, Optional, Regexp)
from app.models import State, User, Provider, Review, Category

def state_list():
    """Query db to populate state list on forms."""
    return [(s.name, s.name) for s in State.query.order_by("name")]

def category_list():
    """Query db to populate state list on forms."""
    return [(c.name, c.name) for c in Category.query.order_by("name")]

class AddressField(FlaskForm):
    line1 = StringField("Street Address", validators=[DataRequired()])
    line2 = StringField("Address Line 2")
    city = StringField("City", validators=[DataRequired()])
    state = SelectField("State", choices=state_list(), validators=[DataRequired()])
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

class ReviewForm(FlaskForm):
    """Form to submit review."""
    category = SelectField("Service Category", choices=category_list(), 
                           validators=[DataRequired()])
    provider = SelectField("Provider Name", choices=[],
                           validators=[DataRequired()])
    rating = RadioField("Rating", choices=[
                        (5, "***** (Highest quality work)"),
                        (4, "**** (Above Average)"), 
                        (3, "*** (Satisfied - should be default choice"),
                        (2, "** (Below Average)"),
                        (1, "* (Stay away from!)")],
                        validators=[DataRequired()] 
                        )
    description = StringField("Service Description")
    service_date = DateField("Service Date")
    comments = TextAreaField("Comments")
    pictures = FileField("Picture")
    submit = SubmitField("Submit")

class AddProviderForm(FlaskForm):
    """Form to add new provider."""
    name = StringField("First Name", validators=[DataRequired()])
    category = SelectMultipleField("Category", choices=category_list(), validators=[DataRequired()])
    address = FormField(AddressField)
    telephone = StringField("Telephone", validators=[DataRequired(),
                Regexp("[(]?[0-9]{3}[)-]{0,2}[0-9]{3}[-]?[0-9]{4}")])
    email = StringField("Email", validators=[Email()])
    submit = SubmitField("Submit")
   