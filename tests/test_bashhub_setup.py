
import uuid
import socket
from bashhub.bashhub_setup import  handle_system_information
from bashhub import bashhub_setup
import unittest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

def randomnode():
	return 1 << 40
def getnode():
	return 1


class BashhubSetupTest(unittest.TestCase):

	def test_get_mac_addresss(self):
		# Assuming uuid works
		test_mac = bashhub_setup.get_mac_address()
		assert str(uuid.getnode()) == test_mac

		# with uuid returning random
		uuid.getnode = randomnode
		hostname_mac = bashhub_setup.get_mac_address()
		assert str(abs(hash(socket.gethostname()))) == hostname_mac

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

