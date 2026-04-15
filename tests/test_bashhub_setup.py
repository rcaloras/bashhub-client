
import uuid
import socket
from bashhub.bashhub_setup import  handle_system_information, get_new_user_information, update_system_info
from bashhub.model.system import System
from bashhub import bashhub_setup
import unittest
import os
import pytest

from unittest.mock import patch, MagicMock

RANDOM_NODE = 1 << 40  # multicast bit set → uuid.getnode() "failed"

CI_UNSUPPORTED = os.getenv('CI_UNSUPPORTED', 'false').lower() == 'true'


def _make_system(name='my-box', mac='123456789', hostname='my-box'):
	return System(
		name=name,
		mac=mac,
		id='sys-id',
		created=0,
		updated=0,
		hostname=hostname,
		client_version='test',
	)


class BashhubSetupTest(unittest.TestCase):

	@pytest.mark.skipif(CI_UNSUPPORTED, reason='uuid for mac address not supported on github actions')
	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=123456789)
	@patch('bashhub.bashhub_setup.get_from_config', return_value='')
	def test_get_mac_addresss(self, _mock_cfg, _mock_node):
		# Assuming uuid works and no cached mac in config
		test_mac = bashhub_setup.get_mac_address()
		assert test_mac == '123456789'

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=RANDOM_NODE)
	@patch('bashhub.bashhub_setup.get_from_config', return_value='')
	def test_get_mac_addresss_where_uuid_is_random(self, _mock_cfg, _mock_node):
		# with uuid returning random and no cached mac in config
		hostname_mac = bashhub_setup.get_mac_address()
		assert socket.gethostname() == hostname_mac

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=RANDOM_NODE)
	@patch('bashhub.bashhub_setup.get_from_config', return_value='cached-mac-from-config')
	def test_get_mac_address_prefers_config(self, _mock_cfg, _mock_node):
		# When a mac is cached in config, we should use it and ignore uuid.getnode()
		assert bashhub_setup.get_mac_address() == 'cached-mac-from-config'

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config', return_value='')
	@patch('bashhub.bashhub_setup.rest_client')
	@patch('bashhub.bashhub_setup.input', side_effect=['sys1', 'sys2', "sys3", "sys4"])
	def test_handle_system_information_failure(self, mock_input, mock_rest_client, _mock_cfg, _mock_write, _mock_node):

		# Should retry 4 times with bad results
		mock_rest_client.get_system_information = MagicMock()
		mock_rest_client.get_system_information.return_value = None
		mock_rest_client.register_system = MagicMock()
		mock_rest_client.register_system.return_value = None

		result = handle_system_information('some-user', 'some-password')
		assert result == (None, None)
		assert mock_rest_client.register_system.call_count == 4

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config', return_value='')
	@patch('bashhub.bashhub_setup.rest_client')
	@patch('bashhub.bashhub_setup.input', side_effect=['sys1', 'sys2', "sys3", "sys4"])
	def test_handle_system_information_succeed_second(self, mock_input, mock_rest_client, _mock_cfg, mock_write, _mock_node):

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
		# The successful register should have pinned the mac into config.
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 1


class HandleSystemInformationMacTest(unittest.TestCase):
	"""Covers the mac-stabilization + self-heal behavior in the setup path."""

	def _cfg(self, mac='', system_name=''):
		"""Return a get_from_config side_effect that looks up by key."""
		values = {'mac': mac, 'system_name': system_name}
		return lambda key, default='': values.get(key, default)

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	def test_mac_lookup_happy_path_writes_config(self, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# Fresh-ish run: no cached mac, no cached system_name, but the
		# server recognizes us by the freshly-computed mac.
		mock_cfg.side_effect = self._cfg()
		found = _make_system(name='existing-box', mac='111222333')
		mock_rest_client.get_system_information.return_value = found
		mock_rest_client.login_user.return_value = 'token-string'

		result = handle_system_information('u', 'p')

		assert result == ('token-string', 'existing-box')
		# Should not reconcile-PATCH when the mac already matches.
		mock_rest_client.patch_system.assert_not_called()
		# Should pin the agreed-on mac into config.
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 1

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	def test_name_fallback_self_heals_drifted_mac(self, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# Stored system_name exists, mac has drifted: server returns
		# the system via name-fallback with a different mac, client
		# should reconcile with a PATCH and write the new mac.
		mock_cfg.side_effect = self._cfg(system_name='my-box')
		# Server-side mac differs from what we just computed — this
		# simulates the drift case.
		drifted_server_mac = 'server-mac-from-before-drift'
		found = _make_system(name='my-box', mac=drifted_server_mac)
		mock_rest_client.get_system_information.return_value = found
		mock_rest_client.login_user.return_value = 'token-string'
		mock_rest_client.patch_system.return_value = 200

		result = handle_system_information('u', 'p')

		assert result == ('token-string', 'my-box')
		# The GET should pass both mac and the stored name.
		call_kwargs = mock_rest_client.get_system_information.call_args.kwargs
		assert call_kwargs.get('name') == 'my-box'
		assert call_kwargs.get('mac')  # non-empty
		# Should reconcile by PATCHing against the server's old mac.
		mock_rest_client.patch_system.assert_called_once()
		patch_args = mock_rest_client.patch_system.call_args
		assert patch_args.args[1] == drifted_server_mac
		assert patch_args.args[0].mac == call_kwargs.get('mac')
		# Should pin the reconciled mac into config.
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 1

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	@patch('bashhub.bashhub_setup.input', return_value='brand-new-box')
	def test_brand_new_registration_writes_config(self, _mock_input, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# No cached anything, server doesn't recognize us, register succeeds.
		mock_cfg.side_effect = self._cfg()
		mock_rest_client.get_system_information.return_value = None
		mock_rest_client.register_system.return_value = 'brand-new-box'
		mock_rest_client.login_user.return_value = 'token-string'

		result = handle_system_information('u', 'p')

		assert result == ('token-string', 'brand-new-box')
		mock_rest_client.register_system.assert_called_once()
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 1


class UpdateSystemInfoTest(unittest.TestCase):
	"""Covers update_system_info() self-heal + config backfill."""

	def _cfg(self, mac='', system_name=''):
		values = {'mac': mac, 'system_name': system_name}
		return lambda key, default='': values.get(key, default)

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	def test_happy_path_writes_mac_to_config_when_absent(self, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# Healthy user with no cached mac in config: PATCH succeeds
		# and we should backfill mac into config.
		mock_cfg.side_effect = self._cfg(system_name='my-box')
		mock_rest_client.patch_system.return_value = 200

		result = update_system_info()

		assert result == 200
		assert mock_rest_client.patch_system.call_count == 1
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 1

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	def test_happy_path_noop_write_when_mac_already_cached(self, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# Already-stable user with cached mac: PATCH succeeds, no
		# redundant config write.
		mock_cfg.side_effect = self._cfg(mac='already-pinned', system_name='my-box')
		mock_rest_client.patch_system.return_value = 200

		result = update_system_info()

		assert result == 200
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 0

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	def test_self_heal_on_patch_404(self, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# PATCH 404s (drifted mac). With a stored system_name, we
		# should GET by name, then PATCH against the server's mac
		# with the new mac in the body, and backfill config.
		mock_cfg.side_effect = self._cfg(system_name='my-box')
		found = _make_system(name='my-box', mac='server-mac-from-before-drift')
		mock_rest_client.get_system_information.return_value = found
		# First PATCH (against our computed mac) 404s. Second PATCH
		# (against the server's actual mac) succeeds.
		mock_rest_client.patch_system.side_effect = [None, 200]

		result = update_system_info()

		assert result == 200
		assert mock_rest_client.patch_system.call_count == 2
		# Second PATCH should target the server's mac and include
		# the new mac in the body.
		second_call = mock_rest_client.patch_system.call_args_list[1]
		assert second_call.args[1] == 'server-mac-from-before-drift'
		assert second_call.args[0].mac  # non-empty
		mock_rest_client.get_system_information.assert_called_once_with(name='my-box')
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 1

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	def test_no_recovery_when_system_name_missing(self, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# PATCH 404s, no stored system_name -> return None unchanged.
		# Installer will then fall through to `bashhub setup` as today.
		mock_cfg.side_effect = self._cfg()
		mock_rest_client.patch_system.return_value = None

		result = update_system_info()

		assert result is None
		mock_rest_client.get_system_information.assert_not_called()
		assert mock_rest_client.patch_system.call_count == 1
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 0

	@patch('bashhub.bashhub_setup.uuid.getnode', return_value=111222333)
	@patch('bashhub.bashhub_setup.write_to_config_file')
	@patch('bashhub.bashhub_setup.get_from_config')
	@patch('bashhub.bashhub_setup.rest_client')
	def test_self_heal_fails_when_name_lookup_misses(self, mock_rest_client, mock_cfg, mock_write, _mock_node):
		# PATCH 404s, stored name exists but server's name-lookup
		# also misses (rare but possible) -> return None.
		mock_cfg.side_effect = self._cfg(system_name='my-box')
		mock_rest_client.patch_system.return_value = None
		mock_rest_client.get_system_information.return_value = None

		result = update_system_info()

		assert result is None
		# Only one PATCH attempt — we never got a server mac to retry with.
		assert mock_rest_client.patch_system.call_count == 1
		mac_writes = [
			call for call in mock_write.call_args_list
			if call.args and call.args[0] == 'mac'
		]
		assert len(mac_writes) == 0


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

