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


def dollar_filter(data):
    if data is None or type(data) == int:
        return data
    else:
        try:
            dollar_re = re.compile(r'^[\s$]*(?P<num>[\d]+)')
            num = dollar_re.search(data).group('num')
            return num
        except AttributeError:
            raise ValidationError('Entered value must be an integer or $ value')


def int_filter(data):
    if data is None:
        return data
    else:
        return int(data)
