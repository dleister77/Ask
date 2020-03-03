import os
import re

from flask import session
from flask_login import current_user
from flask_wtf import FlaskForm
from magic import from_file, from_buffer
from wtforms import (StringField, BooleanField, SelectField,
     SubmitField, FormField, TextAreaField, RadioField, SelectMultipleField,
     MultipleFileField, HiddenField, FloatField, IntegerField)
from wtforms.validators import (DataRequired, InputRequired, Email, \
                                ValidationError, Optional, NumberRange,\
                                Regexp, InputRequired, StopValidation, Length)
from wtforms.widgets import HiddenInput
from wtforms.ext.dateutil.fields import DateField

from app.auth.forms import AddressField
from app.models import Address, Category, Provider, Sector, State, Review,\
                       Picture, User, Conversation
from app.utilities.forms import MultiCheckboxField
from app.utilities.helpers import url_check, url_parse


def Picture_Upload_Check(form, field):
    """Validate picture upload.
    
    Verify that picture is image type and less than 7.5mb. Stop validation if 
    no file submitted.
    
    Args:
        form (wtf form): form that file upload field is in
        field (form field): file upload field
    
    Returns:
        None
        
    Raises:
        Stop Validation: If no files are uploaded
        ValidationError: If file is not image type or file size > 7.5mb
    
    """
    allowed = ['jpeg', 'png', 'gif', 'bmp', 'tiff']
    if field.data is None or field.data == "" or not field.data[0]:
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
    """Factory function to compare field value to another field.

    Args:
        ComparisonField (Field): Field that current field value is being
            compared to

    Returns:
        _not EqualTo (function): Callable function comparing calling field to
            field passed into factor as argument
    
    Raises:
        ValidationError: If both values are True
    """

    def _notEqualTo(form, field):
        compare_field = getattr(form, comparisonField)
        message = f"{field.label.text} and {compare_field.label.text} are not allowed to both be selected."
        if field.data is True and compare_field.data is True:
            raise ValidationError(message)
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
        if field.name == "telephone":
            data = re.sub('\D+', '', field.data)
        else:
            data = field.data
        entity = modelClass.query.filter(columnName == data).first()
        if entity is not None:
            raise ValidationError(message)
    return _unique_check

def unknown_check(form, field):
    """Removes validation errors from field if address unknown is checked."""
    print("unknown check called")
    if form.unknown.data is True:
        field.errors.clear()
        raise StopValidation()

def gpsVal(form, field):
    """checks that GPS data included if gps selected as location source.

    Args:
        form (wtf form): form that file upload field is in
        field (form field): file upload field
    
    Returns:
        None
        
    Raises:
        ValidationError: If gps selected as source and gps lat/long removed from form.
    """

    if form.location.data == 'gps':
        if field.data in ["", None]:
            raise ValidationError("Must allow access to device location if gps selected as location source.")

def floatCheck(form, field):
    """checks that GPS data not altered to non-numeric type.

    Args:
        form (wtf form): form that file upload field is in
        field (form field): file upload field
    
    Returns:
        None
        
    Raises:
        ValidationError: If gps lat/long altered to non numeric type.
        
    """    

    if form.location.data == "gps" and field.data not in ["", None]:
        try:
            float(field.data)
        except ValueError:
            raise ValidationError("GPS location data must be numeric type.")

class ProviderAddress(AddressField):
    """Subclass of Address to add address unknown checkbox."""
    unknown = BooleanField("Check if full address unknown",
                                        id="addressUnknown",
                                        validators=[Optional()])    
    line1 = StringField("Street Address",
            validators=[unknown_check, 
                InputRequired(message="Street address is required.")])    
    zip = StringField("Zip", 
          validators=[unknown_check, 
              InputRequired(message="Zip code is required.")])

    def populate_choices(self):
        """Populate choices in state drop down."""
        self.state.choices = State.list()

class NonValSelectField(SelectField):
    """Select field with pre-validation removed to allow for client side generated 
       choices.
       """
    def pre_validate(self, form):
        pass


class ReviewForm(FlaskForm):
    """Form to submit review.
    
    Fields:
        name (str): disabled (display only). Name of business being reviewed
        id (int): hidden, id of business being reviewed
        category (select): category for service/business being reviewed
        rating (radio): Numeric rating of 1 to 5 for total quality
        cost (radio): Numeric rating of 1 to 5 based on perceived cost
        description (str): Optional, short description of service provided or 
            business interraction
        service_date (Date): Optional, date of service or interraction w/
            business
        comments (text): Optional, longer description/commentary of review
        picture (File): Optional, add pictures to review
    
    Methods:
        validate_name: checks that submitted id and name match
        validate_category: checks that review category is category of the business
        """

    name = StringField("Provider / Business Name",
                        render_kw = {'readonly':True},
                        validators=[InputRequired(message="Business name is required.")])
    id = HiddenField("Provider Value", 
                     render_kw = {'readonly':True},
                     validators=[InputRequired(message="Business id is required. Do not remove from form submission.")])
    category = SelectField("Category",
                      choices=[],
                      validators=[InputRequired(message="Category is required.")],
                      coerce=int, id="category")    
    rating = RadioField("Overall Rating", choices=[
                        (5, "***** (Highest quality)"),
                        (4, "**** (Above Average)"), 
                        (3, "*** (Satisfied - should be default choice"),
                        (2, "** (Below Average)"),
                        (1, "* (Stay away from!)")],
                        coerce=int,
                        validators=[InputRequired(message="Rating is required.")], 
                        )
    cost = RadioField("Cost- rating", choices=[
                        (5, "$$$$$ (Much higher than competitors)"),
                        (4, "$$$$ (Above Average)"), 
                        (3, "$$$ (Average / should be default choice"),
                        (2, "$$ (Below Average)"),
                        (1, "$ (Significantly less than competitors)")],
                        coerce=int,
                        validators=[InputRequired(message="Cost is required.")] 
                        )
    price_paid = IntegerField("Price Paid", validators=[NumberRange(min=0,
                 message="Dollar cost be greater than 0."), Optional()])
    description = StringField("Service Description", validators=[Optional()])
    service_date = DateField("Service Date", validators=[Optional()])
    comments = TextAreaField("Comments", render_kw={"rows":6}, validators=[Optional()])
    picture = MultipleFileField("Picture", render_kw=({"accept": 'image/*'}),
                                validators=[Picture_Upload_Check, Optional()])
    certify = BooleanField("Reviewer confirms that they have neither received "
                           "compensation for review nor are related (relative, "
                           "employee) to business being reviewed.", 
                           validators=[InputRequired("Review unable to be submitted unless reviewer confirms agreement.")])
    submit = SubmitField("Submit", id="review_submit")

    def validate_name(form, field):
        """Validates name field as well as id hidden field."""
        provider = Provider.query.get(form.id.data)
        if provider == None:
            pass
        elif provider.name != field.data:
            raise ValidationError("Submitted name and id combination are invalid.")
    
    def validate_category(form, field):
        """Checks that category is valid category for provider."""
        id = form.id.data
        if id is None or id == "":
            pass
        else:
            bizCategories = [c.id for c in Provider.query.get(id).categories]
            if field.data not in bizCategories:
                raise ValidationError("Category not valid for business being reviewed.")

class ReviewEditForm(ReviewForm):
    id = HiddenField("Review ID", 
                     render_kw = {'readonly':True},
                     validators=[InputRequired(message="Review id is required. Do not remove from form submission.")])
    
    deletePictures = MultiCheckboxField("Existing Pictures")

    picture = MultipleFileField("New Pictures", render_kw=({"accept": 'image/*'}),
                                validators=[Picture_Upload_Check, Optional()])

    def validate_id(form, field):
        """validates submitted review id is valid"""
        review = Review.query.get(form.id.data)
        if review is None:
            raise ValidationError("Submitted review id is not valid.")

    def validate_name(form, field):
        pass

    def validate_deletePictures(form, field):
        """check that picture id passed corresponds to actual review"""
        
        id = form.id.data
        if id is None or id == "":
            pass
        else:
            review = Review.query.get(form.id.data)
            if review is not None:
                for picID in form.deletePictures.data:
                    picture = Picture.query.get(picID)
                    if picture not in review.pictures:
                        raise ValidationError("Invalid picture submitted for deletion.")
    
    def validate_category(form, field):
        """Checks that category is valid category for provider."""
        id = form.id.data
        if id is None or id == "":
            pass
        else:
            review = Review.query.get(form.id.data)
            if review is not None:
                bizCategories = [c.id for c in review.provider.categories]
                if field.data not in bizCategories:
                    raise ValidationError("Category not valid for business being reviewed.")
    
    def populate_choices(self, review):
        """Populate existing picture checklist"""
        self.deletePictures.choices = [
            (picture.id, picture.name) for picture in review.pictures
        ]
        self.category.choices = [
            (c.id, c.name) for c in review.provider.categories
        ]


class ProviderAddForm(FlaskForm):
    """Form to add new provider.
    
    Fields:
        name (str): name of business
        sector (select): macro sector that business belongs to
        category (select): categories (w/in sector) that business belongs to
        email (str): optional, email address of business
        website (str): optional, website of business
        telepohone (str): telephone number of business
        address-unknown (bool): checked if street address (line1/line2) and zip
            are unknown (i.e. service provider without phyiscal location).  If 
            unchecked, line1 and zip are required. 
        address-line1 (str): 1st address line
        address-line2 (str): optional, 2nd address line
        address-city (str): city name
        address-state (select): address state, select is combination of id,name
        address-zip (str): zip/postal code
    
    Methods:
        validate_name: validator, checks that provider does not already exist by
            checking to see if another provider exists with same name and address
    
    """
    name = StringField("Provider / Business Name", validators=[InputRequired(message="Business name is required.")])
    sector = SelectField("Sector",
                                 choices=Sector.list(), 
                                 validators=[InputRequired(message="Sector is required.")],
                                 coerce=int,
                                 id="sector")   
    category = SelectMultipleField("Category",
                                   choices=Category.list(1),
                                   validators=[InputRequired(message="Category is required.")],
                                   coerce=int,
                                   id="category")
    address = FormField(ProviderAddress)
    email = StringField("Email", validators=[Email(),
                         unique_check(Provider, Provider.email), Optional()])
    website = StringField("Website")
    telephone = StringField("Telephone",
                validators=[InputRequired(message="Telephone number is required."),
                Regexp("[(]?[0-9]{3}[)-]{0,2}\s*[0-9]{3}[-]?[0-9]{4}"), 
                unique_check(Provider, Provider.telephone)])
    submit = SubmitField("Submit", id="provider_submit")

    def validate_name(self, name):
        """Verify business does not already exist.
        Checks to see if business with same name and address already entered.
        """
        p = Provider.query.join(Provider.address)\
                           .filter(Provider.name == self.name.data,
                                   Address.line1 == self.address.line1.data,
                                   Address.line2 == self.address.line2.data,
                                   Address.city == self.address.city.data,
                                   Address.state_id == self.address.state.data,
                                   Address.zip == self.address.zip.data)\
                           .first()
        if p:
            raise ValidationError("Business already exists, please look up "
                "business or use a different name/address.")
    
    def validate_website(self, website):
        """check that url is valid."""
        if website.data != "" and not url_check(website.data):
            raise ValidationError("Invalid website url")

    def populate_choices(self, sector=1):
        """Populate choices for sector and category drop downs."""
        self.sector.choices = Sector.list()
        self.category.choices = Category.list(sector)
        self.address.state.choices = State.list()
        return self

class ProviderSearchForm(FlaskForm):
    """Form to search for providers.
    
    Fields:
        location (select): location source for search
        manual_location (str): manually type in new address
        gpsLat (hidden): records latitude when gps selected as location source
        gpsLong (hidden): record longitude when gps selected as location source
        sector (select): macro sector user is searching (determines categories)
        category (select): micro category that user is searching
        name (str): name of business if searching for specific name
        reviewed_filter(bool): filters out providers with no reviews
        friends_filter (bool): only includes providers reviewed by your friends
        groups_filter (bool): only includes providers reviewed by your groups
        sort (select): choose sort criteria for search results
    
    Methods:
        populate_choices: populates category and location choices prior to form
            validation
        initialize: adds manual existing to location choices if needed


        """
    class Meta:
        csrf = False
    
    location = SelectField("Search Location",
                       choices = [],
                       validators=[InputRequired(message="Search location is required.")],
                       id="location")  
    manual_location = StringField("Enter New Location", validators=[],
                             render_kw={"placeholder":
                             "Street address, city, state"})
    gpsLat = FloatField("New latitude", render_kw={"hidden":True}, id="gpsLat")
    gpsLong = FloatField("New longitude", render_kw={"hidden":True}, id="gpsLong")
    gpsLat = HiddenField("New latitude", validators=[gpsVal, floatCheck], id="gpsLat")
    gpsLong = HiddenField("New longitude", validators=[gpsVal, floatCheck], id="gpsLong")
    searchRange = IntegerField("Search Range (miles)", default=30, validators=[InputRequired('Search range is required.')])
    sector = SelectField("Sector",
                                 choices=Sector.list(), 
                                 coerce=int,
                                 id="sector",
                                 validators=[DataRequired("Sector is required.")]) 
    category = SelectField("Category", id="category", choices=[], 
                           validators=[InputRequired("Category is required.")],
                           coerce=int)
    name = StringField("Provider / Business Name", validators=[Optional()],
                       id="provider_name")
    reviewed_filter = BooleanField("all")
    friends_filter = BooleanField("friends")
    groups_filter = BooleanField("groups")
    sort = SelectField("Sort By",
                        choices=[("rating", "Rating"), ("name", "Name"),
                                ("distance", "Distance")],
                        validators=[InputRequired("Sort criteria is required.")]
                       )
    submit = SubmitField("Submit")

    def validate_searchRange(self, searchRange):
        if searchRange.data < 0:
            raise ValidationError("Search range must be a positive number.")

    def populate_choices(self):
        """populates category and location choices prior to form validation."""
        self.sector.choices = Sector.list()
        self.sector.choices.insert(0, (0, "Choose from list"))
        if self.sector.data:
            self.category.choices = Category.list(self.sector.data)
        else:
            self.category.choices = Category.list(1)
            self.category.choices.insert(0, (0, "Choose from list"))
        self.location.choices = [("home", f"Home - "
                                           f"{current_user.address.line1}, "
                                           f"{current_user.address.city}, "
                                           f"{current_user.address.state.state_short}"),
                                  ("gps", "New - Use GPS"), ("manual", "New - Manually Enter")]
        self.location.default = self.location.choices[0]
        location = session.get('location')
        if location is not None and self.location.data == "manualExisting":
            self.location.choices.insert(0, ("manualExisting", 
                                         f"{location['address']}"))        
        return self
    
    def initialize(self):
        """Update location choices and empty manual location input prior to rendering"""
        location = session.get('location')
        if location is not None and self.location.data=="manual":
            self.location.choices.insert(0, ("manualExisting", 
                                         f"{location['address']}"))
            self.location.data = self.location.choices[0]    
            self.manual_location.data = ""
        return self
    
    def set_default_values(self):
        self.sector.data = 0
        self.category.data = 0
        if self.location.data in [None, 'None']:
            self.location.data = "home"
        self.searchRange.data = 30
        return self
        


class ProviderFilterForm(FlaskForm):
    """Form to apply social filters to provider profile page."""

    class Meta:
        csrf = False
    friends_filter = BooleanField("Friends")
    groups_filter = BooleanField("Groups")
    submit = SubmitField("Update")


class UserMessageForm(FlaskForm):    
    """Form for users to send each other messages."""
    recipient_id = IntegerField("to_id", id="msg_new_recipient_id",
                   render_kw = {"readonly": True, "hidden": True},
                   validators=[InputRequired("Recipient ID is required.")])
    conversation_id = IntegerField("conversation_id", id="msg_new_conversation_id",
                      render_kw = {"readonly": True, "hidden": True},
                      validators=[Optional(strip_whitespace=True)]
                      )
    recipient = StringField("To",
                            id="msg_new_recipient", render_kw={"readonly": True},
                             validators=[InputRequired("Recipient is required.")])
    subject = StringField("Subject", id="msg_new_subject")
    body = TextAreaField("Message Body", render_kw=dict(rows=6),
                         id="msg_new_body",
                          validators=[Length(min=0, max=1000)])
    submit = SubmitField("Send", id="submit_msg")

    def validate_recipient_id(form, field):
        recipient = User.query.filter_by(id=field.data).first()
        if recipient is None:
            raise ValidationError(f"User ({form.recipient.data}) does not exist.")

    def validate_conversation_id(form, field):
        if field.data is None:
            pass
        else:
            conversation = Conversation.query.filter_by(id=field.data).first()
            if conversation is None:
                raise ValidationError("Message conversation does not exist. "
                                       "Please refresh and try again")