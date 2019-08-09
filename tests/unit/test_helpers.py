from app.utilities.helpers import name_check
from app.models import Provider, Review
import os
import pytest

def test_namecheck():
    test_path = os.path.join('instance', 'tests', 'photos', 'source').replace("\\", "/")
    filename = 'test1.jpg'
    filename = name_check(test_path, filename)
    assert filename == 'test1.jpg'
    filename = 'test.jpg'
    filename = name_check(test_path, filename)
    assert filename == 'test_1.jpg'





