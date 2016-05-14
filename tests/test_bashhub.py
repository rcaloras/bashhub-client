import os

import click
from click.testing import CliRunner

from bashhub.bashhub import bashhub
from bashhub.version import __version__
from bashhub.bashhub import rest_client
from bashhub.bashhub import bashhub_globals


def test_bashhub_save():
    def print_failed(command):
        print("Failed")
        pass

    rest_client.save_command = print_failed

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
