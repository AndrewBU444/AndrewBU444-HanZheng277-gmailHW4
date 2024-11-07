import pytest
import requests
from unittest.mock import patch
from meal_max.utils.random_utils import get_random

#def test_get_random_success():

#def test_get_random_value_error():

def test_get_random_timeout(): #Test that get_random raises RuntimeError on a timeout
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        with pytest.raises(RuntimeError, match="Request to random.org timed out"):
            get_random()

#def test_get_random_request_exception():

