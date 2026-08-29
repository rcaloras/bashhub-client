import os
from importlib.metadata import version as installed_version
from pathlib import Path

import pytest
from click.testing import CliRunner

from bashhub.bashhub import bashhub, bashhub_globals, download_installer, rest_client
from bashhub.version import __version__


def test_bashhub_save(monkeypatch):
    def print_failed(command):
        print("Failed")
        pass

    # Restore afterwards: assigning directly left the stub in place for every
    # later test in the run, including the save_command tests in
    # test_rest_client.py.
    monkeypatch.setattr(rest_client, 'save_command', print_failed)

    runner = CliRunner()
    args = ['save', 'echo "Running bashhub tests"', '/tmp', '1', '100000', '1']

    ignored_command = ['save', 'echo "Running bashhub tests" #ignore', '/tmp',
                       '1', '100000', '1']

    # Should omit saving if save_commands is set
    bashhub_globals.BH_SAVE_COMMANDS = False
    result = runner.invoke(bashhub, args)
    assert '' == result.output

    bashhub_globals.BH_SAVE_COMMANDS = True

    # Should omit saving if #ignore is set
    result = runner.invoke(bashhub, ignored_command)
    assert '' == result.output

    # Should omit saving a command if BH_FILTER regex is set
    bashhub_globals.BH_FILTER = 'echo'
    result = runner.invoke(bashhub, args)
    assert '' == result.output

    def no_auth_token():
        return ''

# Should not try to save a command if we don't have an auth token

    bashhub_globals.BH_AUTH = no_auth_token
    result = runner.invoke(bashhub, ['save', 'date', '/tmp', '1', '1000', '1'])
    error_message = "No auth token found. Run 'bashhub setup' to login.\n"
    assert error_message == result.output


def test_bashhub_version():
    runner = CliRunner()
    result = runner.invoke(bashhub, ['version'])
    assert __version__ in result.output


def test_bashhub_version_matches_installed_distribution():
    assert __version__ == installed_version('bashhub')


def test_bashhub_update_writes_decoded_installer_response(monkeypatch):
    script = b'#!/bin/bash\necho setup\n'
    calls = []

    class GitHubResponse:
        status_code = 200

    class SetupResponse:
        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            assert chunk_size == 8192
            return [script]

    def get(url, stream=False):
        calls.append((url, stream))
        if 'github.com' in url:
            return GitHubResponse()
        return SetupResponse()

    def call(args):
        with open(args[2], 'rb') as installer:
            assert installer.read() == script
        assert args == ['bash', '-e', 'update-bashhub.sh', '3.1.0rc2']
        return 0

    monkeypatch.setattr('bashhub.bashhub.requests.get', get)
    monkeypatch.setattr('bashhub.bashhub.subprocess.call', call)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(bashhub, ['update', '3.1.0rc2'])

    assert result.exit_code == 0
    assert ('https://bashhub.com/setup?version=3.1.0rc2', True) in calls


@pytest.mark.skipif(
    not os.getenv('functional_test'),
    reason='requires the production Bashhub setup endpoint',
)
def test_bashhub_update_downloads_production_installer(tmp_path):
    installer = tmp_path / 'update-bashhub.sh'

    download_installer('https://bashhub.com/setup', str(installer))

    script = Path(installer).read_bytes()
    assert script.startswith(b'#!/bin/bash')
    assert b'install_bashhub' in script
