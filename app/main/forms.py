import os
import re

from flask_login import current_user
from flask_wtf import FlaskForm
from magic import from_file, from_buffer
from wtforms import (StringField, BooleanField, SelectField,
     SubmitField, FormField, TextAreaField, RadioField, SelectMultipleField,
     MultipleFileField)
from wtforms.validators import (DataRequired, Email, ValidationError, Optional,
 Regexp, InputRequired, StopValidation)
from wtforms.ext.dateutil.fields import DateField

from app.auth.forms import AddressField
from app.models import Address, Category, Provider, Sector, State


def Picture_Upload_Check(form, field):
    """Verify that picture is image type and less than 7.5mb.
       Stop validation if no file submitted."""
    print("picture upload checking")
    print(f"current user {current_user}")
    allowed = ['jpeg', 'png', 'gif', 'bmp', 'tiff']
    print("picture content:" , field.data)
    if field.data is None or field.data == "" or not field.data[0]:
        print("didn't find picture")
        field.errors[:] = []
        raise StopValidation
    for file in field.data:
        print("checking picture file: ", file)
        file_type = from_buffer(file.read(), mime=True).split('/')[1]
        size = file.tell()
        if file_type not in allowed:
            print("need image file")
            raise ValidationError("Please choose an image file.")
        if size > 7500000:
            print("too big")
            raise ValidationError("Please reduce file size to less than 7.5mb.")

def NotEqualTo(comparisonField):

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
        print(current_user)
        print("unique checking ", field.name)
        key = {"email": "Email address",
               "telephone": "Telephone number",
               "name":"Name"}
        message = f"{key[field.name]} is already registered."
        if field.name == "telephone":
            data = re.sub('\D+', '', field.data)
        else:
            data = field.data
            print("data: ", data)
        entity = modelClass.query.filter(columnName == data).first()
        print(f"Data: {data}")
        print(f"entity: {entity}")
        if entity is not None:
            print("raising error")
            raise ValidationError(message)
    return _unique_check


class NonValSelectField(SelectField):
    """Select field with validation removed to allow for client side generated 
       choices.
       """
    def pre_validate(self, form):
        pass


class ReviewForm(FlaskForm):
    """Form to submit review."""
    sector = SelectField("Sector", choices=Sector.list(), 
                           validators=[DataRequired(message="Sector is required.")], coerce=int,
                           id="provider_sector")   
    category = SelectField("Category", choices=[], 
                           validators=[DataRequired(message="Category is required.")], coerce=int,
                           id="provider_category")
    name = NonValSelectField("Provider Name", choices=[], coerce=int,
                             validators=[DataRequired(message="Provider name is required.")],
                             id="provider_name")
    rating = RadioField("Rating", choices=[
                        (5, "***** (Highest quality)"),
                        (4, "**** (Above Average)"), 
                        (3, "*** (Satisfied - should be default choice"),
                        (2, "** (Below Average)"),
                        (1, "* (Stay away from!)")],
                        coerce=int,
                        validators=[DataRequired(message="Rating is required.")] 
                        )
    cost = RadioField("Cost", choices=[
                        (5, "$$$$$ (Much higher than competitors)"),
                        (4, "$$$$ (Above Average)"), 
                        (3, "$$$ (Average / should be default choice"),
                        (2, "$$ (Below Average)"),
                        (1, "$ (Significantly less than competitors)")],
                        coerce=int,
                        validators=[DataRequired(message="Cost is required.")] 
                        )
    description = StringField("Service Description", validators=[Optional()])
    service_date = DateField("Service Date", validators=[Optional()])
    comments = TextAreaField("Comments", validators=[Optional()])
    picture = MultipleFileField("Picture", render_kw=({"accept": 'image/*'}),
                                validators=[Picture_Upload_Check, Optional()])
    submit = SubmitField("Submit")

    def validate_name(self, name):
        """Verify submitted name came from db."""
        category = Category.query.filter_by(id=self.category.data).first()
        if category is None:
            pass
        else:
            provider_list = (Provider.query
                            .filter(Provider.categories.contains(category))
                            .order_by(Provider.name).all())
            provider_list = [provider.id for provider in provider_list]
            if name.data not in provider_list:
                raise ValidationError("Please choose a provider from the list.")

class ProviderAddForm(FlaskForm):
    """Form to add new provider."""
    name = StringField("Provider / Business Name", validators=[DataRequired(message="Provider name is required.")])
    sector = SelectField("Sector",
                                 choices=Sector.list(), 
                                 validators=[DataRequired(message="Sector is required.")],
                                 coerce=int,
                                 id="provider_sector")   
    category = SelectMultipleField("Category",
                                   choices=[],
                                   validators=[DataRequired(message="Category is required.")],
                                   coerce=int,
                                   id="provider_category")
    address = FormField(AddressField)
    email = StringField("Email", validators=[Email(),
                         unique_check(Provider, Provider.email), Optional()])
    telephone = StringField("Telephone",
                validators=[DataRequired(message="Telephone number is required."),
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
            raise ValidationError("Provider already exists, please select a new name.")
class ProviderSearchForm(FlaskForm):
    """Form to search for providers."""
    class Meta:
        csrf = False
    sector = SelectField("Sector",
                                 choices=Sector.list(), 
                                 validators=[DataRequired(message="Sector is required.")],
                                 coerce=int,
                                 id="provider_sector")
    category = SelectField("Category", choices=[], 
                           validators=[DataRequired(message="Category is required.")],
                           coerce=int, id="provider_category")
    city = StringField("City", validators=[DataRequired(message="City is required.")])
    state = SelectField("State", choices=State.list(),
                         validators=[DataRequired(message="State is required.")], coerce=int)
    friends_only = BooleanField("Friends Only", validators=[NotEqualTo('groups_only')])
    groups_only = BooleanField("Groups Only", validators=[NotEqualTo('friends_only')])
    submit = SubmitField("Submit")

class ProviderFilterForm(FlaskForm):
    """Form to apply social filters to provider profile page."""

    class Meta:
        csrf = False
    
    friends_only = BooleanField("Friends Only",
                                validators=[NotEqualTo('groups_only')],
                                false_values = (False, 'false','False', ''))
    groups_only = BooleanField("Groups Only",
                               validators=[NotEqualTo('friends_only')],
                               false_values = (False, 'false', 'False', ''))
    submit = SubmitField("Update")