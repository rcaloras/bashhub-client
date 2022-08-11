
import uuid
import socket
from bashhub.bashhub_setup import  handle_system_information
from bashhub import bashhub_setup
import unittest
import os
import pytest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

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

