from flask import current_app
from flask_login import current_user
from flask_wtf import FlaskForm
from magic import from_file, from_buffer
import os
from wtforms import (StringField, BooleanField, SelectField,
     SubmitField, FormField, TextAreaField, RadioField, SelectMultipleField,
     MultipleFileField)
from wtforms.validators import (DataRequired, Email, ValidationError, Optional,
 Regexp, InputRequired, StopValidation)
from wtforms.ext.dateutil.fields import DateField
from app.models import State, Provider, Category

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

def Picture_Upload_Check(form, field):
    """Verify that picture is image type and less than 7.5mb.
       Stop validation if no file submitted."""
    print("picture upload checking")
    allowed = ['jpeg', 'png', 'gif', 'bmp', 'tiff']
    print("picture content:" , field.data)
    if not field.data[0]:
        print("didn't find picture")
        field.errors[:] = []
        raise StopValidation
    for file in field.data:
        print("checking picture file")
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
        key = {"email": "Email address",
               "telephone": "Telephone number",
               "name":"Name"}
        message = f"{key[field.name]} is already registered."
        entity = modelClass.query.filter(columnName == field.data).first()
        if entity is not None:
            raise ValidationError(message)
    return _unique_check


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
    state = SelectField("State", choices=state_list(), coerce=int,
                         validators=[DataRequired()])
    zip = StringField("Zip", validators=[DataRequired()])

    def validate_zip(form, field):
        if len(field.data) != 5:
            raise ValidationError('Please enter 5 digit zip code.')
        elif not field.data.isdigit():
            raise ValidationError('Only include numbers in zip code.')


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

class ProviderSearchForm(FlaskForm):
    """Form to search for providers."""
    class Meta:
        csrf = False
        

    category = SelectField("Category", choices=category_list(), 
                           validators=[DataRequired()], coerce=int)
    city = StringField("City", validators=[DataRequired()])
    state = SelectField("State", choices=state_list(),
                         validators=[DataRequired()], coerce=int)
    friends_only = BooleanField("Friends Only", validators=[NotEqualTo('groups_only')])
    groups_only = BooleanField("Groups Only", validators=[NotEqualTo('friends_only')])
    submit = SubmitField("Submit")
