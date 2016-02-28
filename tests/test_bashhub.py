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
    args = ['save',
            'echo "Running bashhub tests"',
            '/tmp',
            '1',
            '100000',
            '1']

    ignored_command = ['save',
            'echo "Running bashhub tests" #ignore',
            '/tmp',
            '1',
            '100000',
            '1']

    # Should omit saving if #ignore is set
    result = runner.invoke(bashhub, ignored_command)
    assert '' == result.output

    # Should omit saving a command if BH_FILTER regex is set
    bashhub_globals.BH_FILTER = 'echo'
    result = runner.invoke(bashhub, args)
    assert '' == result.output

def test_bashhub_version():
    runner = CliRunner()
    result = runner.invoke(bashhub, ['version'])
    assert __version__ in result.output
