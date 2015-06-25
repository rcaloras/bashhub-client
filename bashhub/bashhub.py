#!/usr/bin/python
from time import *
import click
import traceback
import dateutil.parser
import sys
import os

from model import Command
from model import UserContext
import rest_client
import bashhub_setup
from bashhub_globals import *
from version import __version__
import shutil
import requests
import subprocess
import shell_utils
from view.status import *

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Bashhub %s' % __version__)
    ctx.exit()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-V', '--version', default=False, is_flag=True, callback=print_version,
        help='Display version', expose_value=False, is_eager=True)
def bashhub():
    """Bashhub command line client"""
    pass

@bashhub.command()
def version():
    """Display version"""
    click.echo('Bashhub %s' % __version__)

@bashhub.command()
@click.argument('command', type=str)
@click.argument('path', type=click.Path(exists=True))
@click.argument('pid', type=long)
@click.argument('process_start_time', type=long)
@click.argument('exit_status', type=int)
def save(command, path, pid, process_start_time, exit_status):
    """Save a command to bashhub.com"""

    pid_start_time = unix_time_to_epoc_millis(process_start_time)
    command = command.strip()

    # Check if we should ignore this commannd or not.
    if "#ignore" in command:
        return

    context = UserContext(pid, pid_start_time, BH_USER_ID, BH_SYSTEM_ID)
    command = Command(command, path, exit_status, context)
    rest_client.save_command(command)

@bashhub.command()
def setup():
    """Run bashhub user and system setup"""
    bashhub_setup.main()

@bashhub.command()
def status():
    """Stats for this session and user"""
    # Get our user and session information from our context
    user_context = shell_utils.build_user_context()
    status_view = rest_client.get_status_view(user_context)
    click.echo(build_status_view(status_view))

@bashhub.command()
@click.argument('version', type=str, default="")
def update(version):
    """Update your bashhub installation"""

    if version !=  "":
         github = "https://github.com/rcaloras/bashhub-client/archive/{0}.tar.gz".format(version)
         response = requests.get(github)
         if response.status_code is not 200:
             click.echo("Invalid version number {0}".format(version))
             sys.exit(1)

    url = 'http://bashhub.com/setup'
    response = requests.get(url, stream=True)
    filename = 'update-bashhub.sh'
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    shell_command = "bash -e {0} {1}".format(filename, version)
    subprocess.call(shell_command, shell=True)
    os.remove(filename)

@bashhub.group()
def util():
    """Misc utils used by bashhub"""
    pass

@util.command()
def update_system_info():
    """Updates system info for bashhub.com"""
    bashhub_setup.update_system_info(BH_SYSTEM_ID)

@util.command()
@click.argument('date_string', type=str)
def parsedate(date_string):
    """date string to seconds since the unix epoch"""
    try:
        date = dateutil.parser.parse(date_string)
        unix_time = int(mktime(date.timetuple()))
        click.echo(unix_time)
    except Exception as e:
        # Should really log an error here
        click.echo(0)

def unix_time_to_epoc_millis(unix_time):
    return int(unix_time)*1000

def main():
    try:
        bashhub()
    except Exception as e:
        formatted = traceback.format_exc(e)
        click.echo("Oops, look like an exception occured: " + str(e))
        sys.exit(1)

main()
