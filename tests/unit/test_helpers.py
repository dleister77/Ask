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

# def test_pag_urls(test_db):
#     p = Provider.query.filter_by(id=1).first()
#     pag_args = {"name": p.name, "id": p.id}
#     r = p.profile_reviews().paginate(1, 1, False)
#     pag_urls = pagination_urls(r, 'main.provider', pag_args)
#     assert pag_urls['next'] == 'localhost:5000/provider/Douthit-Electrical/1?page=2'



