from app import db
from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from magic import from_file, from_buffer
import os
from wtforms import (StringField, PasswordField, BooleanField, SelectField,
     SubmitField, FormField, FieldList, TextAreaField,
     RadioField, SelectMultipleField, MultipleFileField, HiddenField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
 ValidationError, Optional, Regexp, InputRequired, StopValidation)
from wtforms.ext.dateutil.fields import DateField
from app.models import State, User, Provider, Review, Category, Group
from werkzeug import FileStorage

def state_list():
    """Query db to populate state list on forms."""
    return [(s.name, s.name) for s in State.query.order_by("name")]

def category_list():
    """Query db to populate state list on forms."""
    return [(c.id, c.name) for c in Category.query.order_by("name")]

def Picture_Upload_Check(form, field):
    """Verify that picture is image type and less than 7.5mb.
       Stop validation if no file submitted."""
    allowed = ['jpeg', 'png', 'gif', 'bmp', 'tiff']
    if not field.data[0]:
        field.errors[:] = []
        raise StopValidation
    for file in field.data:
        file_type = from_buffer(file.read(), mime=True).split('/')[1]
        size = file.tell()
        if file_type not in allowed:
            raise ValidationError("Please choose an image file.")
        if size > 7500000:
            raise ValidationError("Please reduce file size to less than 7.5mb.")

def NotEqualTo(comparisonField):

    def _notEqualTo(form, field):
        compare_field = getattr(form, comparisonField)
        message = f"{field.label.text} and {compare_field.label.text} are not allowed to both be selected."
        if field.data is True and compare_field.data is True:
            print("invalid")
            raise ValidationError(message)
        print("valid")
    return _notEqualTo

def unique_check(modelClass, columnName):
    """validate that no other entity in class registered for field.
    inputs:
        modelClass: db model class to query
        columnName: db column in modelclass.columname format
    """
    
    def _unique_check(form, field):
        key = {"email": "Email address",
               "telephone": "Telephone number",
               "name":"Name"}
        message = f"{key[field.name]} is already registered."
        entity = modelClass.query.filter(columnName == field.data).first()
        if entity is not None:
            raise ValidationError(message)
    return _unique_check



def relation_check(relationshipType):
    """validate that not already in relation with item being added.
    Inputs:
        relationshipType: relationship being checked on user (i.e. groups or 
        friends)
        """
    message_dict = {"friends":"Already friends with this person.", 
                    "groups":"Already a member of this group."}
    model_dict = {"friends":User, "groups":Group}

    def _relation_check(form, field):   
        relation = (model_dict[relationshipType].query.filter_by(id=field.data)
                                               .first())
        relation_list = getattr(current_user, relationshipType)
        if relation in relation_list:
            raise ValidationError(message_dict[relationshipType])
    return _relation_check

class NonValSelectField(SelectField):
    """Select field with validation removed to allow for client side generated 
       choices.
       """
    def pre_validate(self, form):
        pass


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
            raise ValidationError("Username already exists, please choose a "
                                  "different name.")


class ReviewForm(FlaskForm):
    """Form to submit review."""
    category = SelectField("Category", choices=category_list(), 
                           validators=[DataRequired()], coerce=int,
                           id="provider_category")
    name = NonValSelectField("Provider Name", choices=[], coerce=int,
                       validators=[InputRequired()], id="provider_name")
    rating = RadioField("Rating", choices=[
                        (5, "***** (Highest quality work)"),
                        (4, "**** (Above Average)"), 
                        (3, "*** (Satisfied - should be default choice"),
                        (2, "** (Below Average)"),
                        (1, "* (Stay away from!)")],
                        coerce=int,
                        validators=[DataRequired()] 
                        )
    description = StringField("Service Description")
    service_date = DateField("Service Date", validators=[Optional()])
    comments = TextAreaField("Comments")
    picture = MultipleFileField("Picture", render_kw=({"accept": 'image/*'}),
                                validators=[Picture_Upload_Check])
    submit = SubmitField("Submit")

    def validate_name(self, name):
        """Verify submitted name came from db."""
        category = Category.query.filter_by(id=self.category.data).first()
        provider_list = (Provider.query
                        .filter(Provider.categories.contains(category))
                        .order_by(Provider.name).all())
        provider_list = [provider.id for provider in provider_list]
        if name.data not in provider_list:
            raise ValidationError("Please choose a provider from the list.")

class ProviderAddForm(FlaskForm):
    """Form to add new provider."""
    name = StringField("Provider Name", validators=[DataRequired()])
    category = SelectMultipleField("Category", choices=category_list(), 
                                    validators=[DataRequired()], coerce=int,
                                    id="modal_category")
    address = FormField(AddressField)
    telephone = StringField("Telephone", validators=[DataRequired(),
                Regexp("[(]?[0-9]{3}[)-]{0,2}[0-9]{3}[-]?[0-9]{4}"), 
                unique_check(Provider, Provider.telephone)])
    email = StringField("Email", validators=[Email(), 
                         unique_check(Provider, Provider.email)])
    submit = SubmitField("Submit", id="modal_submit")

class GroupSearchForm(FlaskForm):
    """Form to search for group."""
    name = StringField("Group Name", id="group_name", validators=[DataRequired()])
    value = HiddenField("Group Value", id="group_value", validators=
                        [DataRequired(), relation_check("groups")])
    submit = SubmitField("Add Group", id="submit-group-add")


class FriendSearchForm(FlaskForm):
    """Form to search for group."""
    name = StringField("Friend Name", id="friend_name", validators=[DataRequired()])
    value = HiddenField("Friend Value", id="friend_value", validators=
                        [DataRequired(), relation_check("friends")])
    submit = SubmitField("Add Friend", id="submit-friend-add")


class GroupCreateForm(FlaskForm):
    """Form to create new group."""
    name = StringField("Group Name", validators=[DataRequired(),
                       unique_check(Group, Group.name)])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Add Group", id="submit_new_group")

class ProviderSearchForm(FlaskForm):
    """Form to search for providers."""
    category = SelectField("Category", choices=category_list(), 
                           validators=[DataRequired()], coerce=int)
    city = StringField("City", validators=[DataRequired()])
    state = SelectField("State", choices=state_list(), validators=[DataRequired()])
    friends_only = BooleanField("Friends Only", validators=[NotEqualTo('groups_only')])
    groups_only = BooleanField("Groups Only", validators=[NotEqualTo('friends_only')])
    submit = SubmitField("Submit")

    # def validate_friends_only(self, friends_only, groups_only):
    #     if self.friends_only.data is True and self.groups_only.data is True:
    #         raise ValidationError("Select only one of friends only or groups only")
    
    # def validate_groups_only(self, groups_only, friends_only):
    #     if self.friends_only.data is True and self.groups_only.data is True:
    #         raise ValidationError("Select only one of friends only or groups only")

    