from collections import namedtuple
import datetime
import pytest

from wtforms.validators import ValidationError

from app.utilities.forms import validate_zip, dollar_filter, validate_date,\
    validate_telephone


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
        ['$ 290', '$290', ' $290 ', '290', 290]
    )
    def test_values(self, data):
        test_case = data
        check = dollar_filter(test_case)
        assert str(check) == '290'
    
    def test_empty(self):
        test_case = '$ '
        check = dollar_filter(test_case)
        assert str(check) == '' 


class TestValidateDate():

    def test_valid(self):
        test_case = form_field(datetime.date.today())
        check = validate_date(None, test_case)
        assert check is None

    def test_future_date(self):
        today = datetime.date.today()
        next_year = datetime.date(today.year + 1, today.month, today.day)
        test_case = form_field(next_year)
        with pytest.raises(ValidationError):
            validate_date(None, test_case)


class TestValidateTelephone():
    @pytest.mark.parametrize(
        'tel', ['704-111-2222', '7041112222', '(704)111-2222', '704 111 2222']
    )
    def test_valid(self, tel):
        test_case = form_field(tel)
        check = validate_telephone(None, test_case)
        assert check is None

    @pytest.mark.parametrize(
        'tel', ['704.111-2222', '70411', '704111122223333', '704-abc-1234']
    )
    def test_invalid(self, tel):
        test_case = form_field(tel)
        with pytest.raises(ValidationError):
            validate_telephone(None, test_case)
