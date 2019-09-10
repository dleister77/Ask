import os

import pytest


from app.utilities.helpers import name_check, disableForm, listToString
from app.utilities.forms import RadioInputDisabled
from app.models import Provider, Review

def test_namecheck():
    test_path = os.path.join('instance', 'tests', 'photos', 'source')
    filename = 'test1.jpg'
    filename = name_check(test_path, filename)
    assert filename == 'test1.jpg'
    filename = 'test.jpg'
    filename = name_check(test_path, filename)
    assert filename == 'test_1.jpg'


def test_disableForm(test_app, dbSession):
    from app.main.forms import ReviewForm
    with test_app.app_context():
        form = ReviewForm()
        disableForm(form)
        checkValue = "disabled"
        for field in form:
            if field.type != "RadioField":
                assert checkValue in field.render_kw
            elif field.type == "RadioField":
                assert field.option_widget.__class__ == RadioInputDisabled
    
def test_listToStringSingle():
    testList = ["Tom"]
    x = listToString(testList)
    assert x == "Tom"

def test_listToStringDouble():
    testList = ["Tom", "Dick"]
    x = listToString(testList)
    assert x == "Tom & Dick"

def test_listToStringTriple():
    testList = ["Tom", "Dick", "Harry"]
    x = listToString(testList)
    assert x == "Tom, Dick & Harry"


