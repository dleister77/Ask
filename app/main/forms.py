import os
import re

from flask_login import current_user
from flask_wtf import FlaskForm
from magic import from_file, from_buffer
from wtforms import (StringField, BooleanField, SelectField,
     SubmitField, FormField, TextAreaField, RadioField, SelectMultipleField,
     MultipleFileField, HiddenField)
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

def unknown_check(form, field):
    """Removes validation errors from field if address unknown is checked."""
    if form.full_address_unknown.data is True:
        field.errors[:] = []
        raise StopValidation()


class ProviderAddress(AddressField):
    """Subclass of Address to allow address unknown checkbox."""
    full_address_unknown = BooleanField("Check if full address unknown",
                                        id="addressUnknown",
                                        validators=[Optional()])    
    line1 = StringField("Street Address",
            validators=[DataRequired(message="Street address is required."),
                                     unknown_check])    
    zip = StringField("Zip", 
          validators=[DataRequired(message="Zip code is required."),
                                   unknown_check])


class NonValSelectField(SelectField):
    """Select field with validation removed to allow for client side generated 
       choices.
       """
    def pre_validate(self, form):
        pass


class ReviewForm(FlaskForm):
    """Form to submit review."""

    name = StringField("Provider / Business Name",
                        render_kw = {'disabled':True})
    id = HiddenField("Provider Value", 
                     render_kw = {'readonly':True},
                     validators=[DataRequired(message="Provider name is required")])
    category = SelectField("Category",
                      choices=[],
                      validators=[DataRequired(message="Category is required.")],
                      coerce=int, id="category")    
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
    submit = SubmitField("Submit", id="review_submit")

    def validate_value(self, name):
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
                                 id="sector")   
    category = SelectMultipleField("Category",
                                   choices=[],
                                   validators=[DataRequired(message="Category is required.")],
                                   coerce=int,
                                   id="category")
    address = FormField(ProviderAddress)
    # service_state = SelectMultipleField("Service Area State",
    #                                     choices=State.list(),
    #                                     validators=[DataRequired(message="Service area state is required.")],
    #                                     coerce=int, id="service_state")
    # service_city = SelectMultipleField("Service Area City",
    #                                     choices=[],
    #                                     validators=[DataRequired(message="Service area city is required.")],
    #                                     coerce=int, id="service_city")
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

    # def _make_address_fields_optional(self):
    #     """Update form to make physical address fields optional for service providers with a service area."""
    #     for field in self.address:
    #         field.validators.append(Optional())

    # def _remove_service_area_fields(self):
    #     """Update form to remove service area for business with physical locations."""
    #     del(self.service_state)
    #     del(self.service_city)


    # def check_service_area_required(self):
    #     """Determine whether service area or address field data required validators need to be removed."""
    #     if self.category.service_area_required is True:
    #         self._make_address_fields_optional()
    #     elif not self.category.service_area_required:
    #         self._remove_service_area_fields()
    #     return self


class ProviderSearchForm(FlaskForm):
    """Form to search for providers."""
    class Meta:
        csrf = False
    sector = SelectField("Sector",
                                 choices=Sector.list(), 
                                 validators=[DataRequired(message="Sector is required.")],
                                 coerce=int,
                                 id="sector")
    category = SelectField("Category", choices=[], 
                           validators=[DataRequired(message="Category is required.")],
                           coerce=int)
    # city = StringField("City",
    #                     validators=[DataRequired(message="City is required.")])
    # state = SelectField("State", choices=State.list(),
    #                      validators=[DataRequired(message="State is required.")], coerce=int)
    name = StringField("Provider / Business Name", validators=[Optional()],
                       id="provider_name")
    reviewed_filter = BooleanField("Reviewed - all")
    friends_filter = BooleanField("Reviewed - friends")
    groups_filter = BooleanField("Reviewed - groups")
    sort = SelectField("Sort By",
                        choices=[("rating", "Rating"), ("name", "Name"),
                                ("distance", "Distance")],
                        default=("rating", "Rating"))
    submit = SubmitField("Submit")

    def populate_choices(self):
        self.category.choices = Category.list(self.sector.data)
        return self

class ProviderFilterForm(FlaskForm):
    """Form to apply social filters to provider profile page."""

    class Meta:
        csrf = False
    friends_filter = BooleanField("Friends")
    groups_filter = BooleanField("Groups")
    submit = SubmitField("Update")