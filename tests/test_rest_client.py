"""Tests for rest_client error message extraction and clean error surfacing."""
import json
import unittest
from unittest.mock import patch, MagicMock

import requests

from bashhub import rest_client
from bashhub.rest_client import _extract_error_message
from bashhub.model import RegisterUser, LoginForm, RegisterSystem


def _mock_response(status_code, text="", json_body=None):
    """Build a minimal mock requests.Response."""
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.text = text if json_body is None else json.dumps(json_body)
    if json_body is not None:
        response.json.return_value = json_body
    else:
        response.json.side_effect = ValueError("no json")
    http_error = requests.exceptions.HTTPError(response=response)
    response.raise_for_status.side_effect = http_error
    return response


class TestExtractErrorMessage(unittest.TestCase):

    def test_plain_text_response(self):
        response = MagicMock()
        response.text = "Username already taken"
        response.json.side_effect = ValueError
        assert _extract_error_message(response, "fallback") == "Username already taken"

    def test_plain_text_is_stripped(self):
        response = MagicMock()
        response.text = "  Bad credentials  \n"
        response.json.side_effect = ValueError
        assert _extract_error_message(response, "fallback") == "Bad credentials"

    def test_drf_detail_json(self):
        response = MagicMock()
        response.text = '{"detail": "Not found."}'
        response.json.return_value = {"detail": "Not found."}
        assert _extract_error_message(response, "fallback") == "Not found."

    def test_drf_field_errors_json(self):
        response = MagicMock()
        body = {"email": ["Enter a valid email address."]}
        response.text = json.dumps(body)
        response.json.return_value = body
        assert _extract_error_message(response, "fallback") == "Enter a valid email address."

    def test_empty_body_returns_fallback(self):
        response = MagicMock()
        response.text = ""
        response.json.side_effect = ValueError
        assert _extract_error_message(response, "fallback") == "fallback"

    def test_unparseable_json_returns_fallback(self):
        response = MagicMock()
        response.text = "{broken json"
        response.json.side_effect = ValueError
        assert _extract_error_message(response, "fallback") == "fallback"


class TestRegisterUserErrors(unittest.TestCase):

    @patch('bashhub.rest_client.requests.post')
    def test_409_prints_server_message(self, mock_post):
        mock_post.return_value = _mock_response(409, text="Username already taken")
        user = RegisterUser("a@b.com", "alice", "password123")

        with patch('builtins.print') as mock_print:
            result = rest_client.register_user(user)

        assert result is None
        mock_print.assert_called_once_with("Username already taken")

    @patch('bashhub.rest_client.requests.post')
    def test_422_prints_server_message(self, mock_post):
        mock_post.return_value = _mock_response(
            422, text="Username must be between 1 and 39 characters")
        user = RegisterUser("a@b.com", "alice", "password123")

        with patch('builtins.print') as mock_print:
            result = rest_client.register_user(user)

        assert result is None
        mock_print.assert_called_once_with(
            "Username must be between 1 and 39 characters")

    @patch('bashhub.rest_client.requests.post')
    def test_500_with_server_message_prints_it(self, mock_post):
        mock_post.return_value = _mock_response(500, text="Internal Server Error")
        user = RegisterUser("a@b.com", "alice", "password123")

        with patch('builtins.print') as mock_print:
            result = rest_client.register_user(user)

        assert result is None
        mock_print.assert_called_once_with("Internal Server Error")

    @patch('bashhub.rest_client.requests.post')
    def test_500_empty_body_prints_generic_message(self, mock_post):
        mock_post.return_value = _mock_response(500, text="")
        user = RegisterUser("a@b.com", "alice", "password123")

        with patch('builtins.print') as mock_print:
            result = rest_client.register_user(user)

        assert result is None
        mock_print.assert_called_once_with(
            "Sorry, an unexpected error occurred. Please try again.")


class TestLoginUserErrors(unittest.TestCase):

    @patch('bashhub.rest_client.requests.post')
    def test_401_prints_hardcoded_message(self, mock_post):
        # Server sends "Bad credentials" but client should show our wording.
        mock_post.return_value = _mock_response(401, text="Bad credentials")
        form = LoginForm("alice", "wrongpassword")

        with patch('builtins.print') as mock_print:
            result = rest_client.login_user(form)

        assert result is None
        mock_print.assert_called_once_with("Incorrect username or password.")

    @patch('bashhub.rest_client.requests.post')
    def test_409_prints_server_message(self, mock_post):
        # Unregistered MAC case.
        mock_post.return_value = _mock_response(
            409,
            text="Mac address unregistered. Please register your system first.")
        form = LoginForm("alice", "password123", mac="aa:bb:cc")

        with patch('builtins.print') as mock_print:
            result = rest_client.login_user(form)

        assert result is None
        mock_print.assert_called_once_with(
            "Mac address unregistered. Please register your system first.")

    @patch('bashhub.rest_client.requests.post')
    def test_500_with_server_message_prints_it(self, mock_post):
        mock_post.return_value = _mock_response(500, text="Server Error")
        form = LoginForm("alice", "password123")

        with patch('builtins.print') as mock_print:
            result = rest_client.login_user(form)

        assert result is None
        mock_print.assert_called_once_with("Server Error")

    @patch('bashhub.rest_client.requests.post')
    def test_500_empty_body_prints_generic_message(self, mock_post):
        mock_post.return_value = _mock_response(500, text="")
        form = LoginForm("alice", "password123")

        with patch('builtins.print') as mock_print:
            result = rest_client.login_user(form)

        assert result is None
        mock_print.assert_called_once_with(
            "Sorry, an unexpected error occurred. Please try again.")


class TestRegisterSystemErrors(unittest.TestCase):

    @patch('bashhub.rest_client.requests.post')
    def test_409_prints_server_message(self, mock_post):
        mock_post.return_value = _mock_response(
            409,
            text="The name: home, is already registered for one of your systems.")
        system = RegisterSystem("home", "aa:bb:cc", "mymac", "3.0.3")

        with patch('builtins.print') as mock_print:
            result = rest_client.register_system(system)

        assert result is None
        mock_print.assert_called_once_with(
            "The name: home, is already registered for one of your systems.")

    @patch('bashhub.rest_client.requests.post')
    def test_500_with_server_message_prints_it(self, mock_post):
        mock_post.return_value = _mock_response(500, text="Server Error")
        system = RegisterSystem("home", "aa:bb:cc", "mymac", "3.0.3")

        with patch('builtins.print') as mock_print:
            result = rest_client.register_system(system)

        assert result is None
        mock_print.assert_called_once_with("Server Error")

    @patch('bashhub.rest_client.requests.post')
    def test_500_empty_body_prints_generic_message(self, mock_post):
        mock_post.return_value = _mock_response(500, text="")
        system = RegisterSystem("home", "aa:bb:cc", "mymac", "3.0.3")

        with patch('builtins.print') as mock_print:
            result = rest_client.register_system(system)

        assert result is None
        mock_print.assert_called_once_with(
            "Sorry, an unexpected error occurred. Please try again.")
