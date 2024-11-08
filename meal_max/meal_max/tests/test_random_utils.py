import pytest
import requests
from unittest.mock import patch, Mock
from meal_max.utils.random_utils import get_random #do I need to modify this path

def test_get_random_success(): #Test that get_random returns a float when the response is valid
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '0.45\n'

    with patch('requests.get', return_value=mock_response):
        result = get_random()
        assert result == 0.45, "Expected the random number to be 0.45"

def test_get_random_value_error(): #Test that get_random raises ValueError when response is not a valid float
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'invalid_text'

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(ValueError, match="Invalid response from random.org"):
            get_random()

def test_get_random_timeout(): #Test that get_random raises RuntimeError on a timeout
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        with pytest.raises(RuntimeError, match="Request to random.org timed out"):
            get_random()

def test_get_random_request_failure():  # Test that get_random raises RuntimeError on request failure
    # Mock the `requests.get` call to raise a general `RequestException`
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error")):
        with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
            get_random()


