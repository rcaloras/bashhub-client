
import uuid
import socket
from bashhub.bashhub_setup import  handle_system_information, get_new_user_information
from bashhub import bashhub_setup
import unittest
import os
import pytest

from unittest.mock import patch, MagicMock

def randomnode():
	return 1 << 40
def getnode():
	return 1

CI_UNSUPPORTED = os.getenv('CI_UNSUPPORTED', 'false').lower() == 'true'

class BashhubSetupTest(unittest.TestCase):

	@pytest.mark.skipif(CI_UNSUPPORTED, reason='uuid for mac address not supported on github actions')
	def test_get_mac_addresss(self):
		# Assuming uuid works
		test_mac = bashhub_setup.get_mac_address()
		assert str(uuid.getnode()) == test_mac

	def test_get_mac_addresss_where_uuid_is_random(self):
		# with uuid returning random
		uuid.getnode = randomnode
		hostname_mac = bashhub_setup.get_mac_address()
		assert socket.gethostname() == hostname_mac

	@patch('bashhub.bashhub_setup.rest_client')
	@patch('bashhub.bashhub_setup.input', side_effect=['sys1', 'sys2', "sys3", "sys4"])
	def test_handle_system_information_failure(self, mock_input, mock_rest_client):

		# Should retry 4 times with bad results
		mock_rest_client.get_system_information = MagicMock()
		mock_rest_client.get_system_information.return_value = None
		mock_rest_client.register_system = MagicMock()
		mock_rest_client.register_system.return_value = None

		result = handle_system_information('some-user', 'some-password')
		assert result == (None, None)
		assert mock_rest_client.register_system.call_count == 4

	@patch('bashhub.bashhub_setup.rest_client')
	@patch('bashhub.bashhub_setup.input', side_effect=['sys1', 'sys2', "sys3", "sys4"])
	def test_handle_system_information_succeed_second(self, mock_input, mock_rest_client):

		# Should register on the second time after failing the first
		mock_rest_client.get_system_information = MagicMock()
		mock_rest_client.get_system_information.return_value = None
		mock_rest_client.register_system = MagicMock()
		mock_rest_client.register_system.side_effect = [None, 'sys2', None, None]
		mock_rest_client.login_user = MagicMock()
		mock_rest_client.login_user.return_value = "token-string"

		result = handle_system_information('some-user', 'some-password')
		assert result == ("token-string", "sys2")
		assert mock_rest_client.register_system.call_count == 2


class GetNewUserInformationTest(unittest.TestCase):
	"""Covers the new-user registration prompt flow with per-field
	validation, password confirmation, and the final 'are these correct?'
	confirmation.
	"""

	@patch('bashhub.bashhub_setup.getpass.getpass')
	@patch('bashhub.bashhub_setup.input')
	def test_happy_path(self, mock_input, mock_getpass):
		# email, username, then confirm "yes"
		mock_input.side_effect = ['alice@example.com', 'alice', 'y']
		# password, confirm password
		mock_getpass.side_effect = ['password123', 'password123']

		result = get_new_user_information()

		assert result.email == 'alice@example.com'
		assert result.username == 'alice'
		assert result.password == 'password123'

	@patch('bashhub.bashhub_setup.getpass.getpass')
	@patch('bashhub.bashhub_setup.input')
	def test_invalid_email_reprompts(self, mock_input, mock_getpass):
		# first email bad, second good, then username, then confirm
		mock_input.side_effect = [
			'not-an-email', 'alice@example.com', 'alice', 'y',
		]
		mock_getpass.side_effect = ['password123', 'password123']

		result = get_new_user_information()

		assert result.email == 'alice@example.com'
		# Three input() calls consumed for email+username before confirm
		assert mock_input.call_count == 4

	@patch('bashhub.bashhub_setup.getpass.getpass')
	@patch('bashhub.bashhub_setup.input')
	def test_invalid_username_reprompts(self, mock_input, mock_getpass):
		# email, bad username (with space), good username, confirm
		mock_input.side_effect = [
			'alice@example.com', 'alice bob', 'alice_bob', 'y',
		]
		mock_getpass.side_effect = ['password123', 'password123']

		result = get_new_user_information()

		assert result.username == 'alice_bob'

	@patch('bashhub.bashhub_setup.getpass.getpass')
	@patch('bashhub.bashhub_setup.input')
	def test_empty_inputs_reprompt(self, mock_input, mock_getpass):
		# empty email then valid; empty username then valid; confirm
		mock_input.side_effect = [
			'', 'alice@example.com', '', 'alice', 'y',
		]
		# empty password then valid password twice (for confirmation)
		mock_getpass.side_effect = ['', 'password123', 'password123']

		result = get_new_user_information()

		assert result.email == 'alice@example.com'
		assert result.username == 'alice'
		assert result.password == 'password123'

	@patch('bashhub.bashhub_setup.getpass.getpass')
	@patch('bashhub.bashhub_setup.input')
	def test_short_password_reprompts(self, mock_input, mock_getpass):
		mock_input.side_effect = ['alice@example.com', 'alice', 'y']
		# too short, then valid + confirmation
		mock_getpass.side_effect = ['short', 'password123', 'password123']

		result = get_new_user_information()

		assert result.password == 'password123'
		assert mock_getpass.call_count == 3

	@patch('bashhub.bashhub_setup.getpass.getpass')
	@patch('bashhub.bashhub_setup.input')
	def test_password_confirmation_mismatch_restarts(self, mock_input, mock_getpass):
		mock_input.side_effect = ['alice@example.com', 'alice', 'y']
		# first pair mismatches -> loop restarts and re-prompts for password
		mock_getpass.side_effect = [
			'password123', 'password999',  # mismatch
			'password123', 'password123',  # match
		]

		result = get_new_user_information()

		assert result.password == 'password123'
		assert mock_getpass.call_count == 4

	@patch('bashhub.bashhub_setup.getpass.getpass')
	@patch('bashhub.bashhub_setup.input')
	def test_confirm_no_restarts_whole_flow(self, mock_input, mock_getpass):
		# First pass: email, username, 'no' to confirm -> recurses
		# Second pass: new email, username, 'yes'
		mock_input.side_effect = [
			'first@example.com', 'firstuser', 'n',
			'second@example.com', 'seconduser', 'y',
		]
		mock_getpass.side_effect = [
			'password123', 'password123',
			'password456', 'password456',
		]

		result = get_new_user_information()

		assert result.email == 'second@example.com'
		assert result.username == 'seconduser'
		assert result.password == 'password456'

