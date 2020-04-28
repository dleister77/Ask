from collections import namedtuple
import pytest

from wtforms.validators import ValidationError

from app.utilities.forms import validate_zip, dollar_filter


form_field = namedtuple('form_field', ['data'])


class TestValidateZip():

    @pytest.mark.parametrize(
        'zip',
        ['28210', '28210-1234', ' 28210 ', ' 28210-1234']
    )
    def test_valid(self, zip):
        test_field = form_field(zip)
        check = validate_zip(None, test_field)
        assert check is None

    @pytest.mark.parametrize(
        'zip',
        ['2821', '28210-12345', '123ab']
    )
    def test_invalid(self, zip):
        test_field = form_field(zip)
        with pytest.raises(ValidationError):
            validate_zip(None, test_field)


class TestDollarFilter():

    @pytest.mark.parametrize(
        'data',
        ['290', '$290', '$290.00', ' $290 ']
    )
    def test_values(self, data):
        test_case = data
        check = dollar_filter(test_case)
        assert check == '290'
