import datetime
import re

from wtforms import SelectMultipleField, widgets
from wtforms.validators import ValidationError
from wtforms.widgets.core import html_params, RadioInput



"""From WTF Forms widget documentation. """
"""http://wtforms.simplecodes.com/docs/1.0.3/widgets.html#custom-widgets"""


def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<ul %s>' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<li><input %s /> ' % html_params(**options))
        html.append(u'<label for="%s">%s</label></li>' % (field_id, label))
    html.append(u'</ul>')
    return u''.join(html)


class RadioInputDisabled(RadioInput):
    """Option widget to render radio field options as disabled."""
    def __call__(self, field, **kwargs):
        kwargs['disabled'] = True
        return super(RadioInputDisabled, self).__call__(field, **kwargs)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def pre_validate(self, form):
        """skip pre-validation"""
        pass


def requiredIf(checkField, checkValue=True):
    """Validator to require field if check Field equals set value"""

    def _requiredIf(form, field):
        field_to_check = getattr(form, checkField)
        message = f"{field.label.text} is required."
        if field_to_check.data == checkValue and field.data is None:
            raise ValidationError(message)
        elif field_to_check.data != checkValue:
            field.errors = []
    return _requiredIf


def validate_zip(form, field):
    zip_re = re.compile(r'^\s*[\d]{5}[ -]{0,3}[\d]{4}\s*$|^\s*[\d]{5}\s*$')
    if zip_re.search(field.data) is None:
        raise ValidationError('Please enter a 5 or 9 digit zip code.')


def validate_date(form, field):
    date = field.data
    if date is not None and date > datetime.date.today():
        raise ValidationError('Date entered is in the future.  Please enter a valid date')


def validate_telephone(form, field):
    tel_re = re.compile(r"[ ]*[(]?[0-9]{3}[)\- ]{0,2}\s*[0-9]{3}[\- ]?[0-9]{4}[ ]*$")
    tel_num = tel_re.match(field.data)
    if tel_num is None:
        raise ValidationError("Please submit telephone number in '(###)###-####' format.")


def dollar_filter(data):
    msg = 'Entered value must be an integer or $ value'
    if data is None or data == '' or type(data) == int:
        return data
    else:
        data = data.strip()
        dollar_re = re.compile(r'\$? ?[\d,]*$')
        check = dollar_re.match(data).group()
        if check is None:
            raise ValidationError(msg)
        else:
            val = re.sub(r'\$ ?', '', data)
            return val


def int_filter(data):
    if data is None or data == '':
        return None
    else:
        return int(data)
