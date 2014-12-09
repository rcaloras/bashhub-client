#!/usr/bin/python
from time import *
import click
import traceback
import dateutil.parser
import sys

from model import Command
from model import UserContext
import rest_client
import bashhub_setup
from bashhub_globals import *
from version import __version__
import shutil
import requests
import subprocess

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Bashhub %s' % __version__)
    ctx.exit()

@click.group()
@click.option('-V', '--version', default=False, is_flag=True, callback=print_version,
        help='Show version and exit', expose_value=False, is_eager=True)

def bashhub():
    """Bashhub command line client"""
    pass


@bashhub.command()
@click.argument('command', type=str)
@click.argument('path', type=click.Path(exists=True))
@click.argument('pid', type=long)
@click.argument('process_start_time', type=long)
def save(command, path, pid, process_start_time):
    """Save a command to bashhub.com"""

    pid_start_time = unix_time_to_epoc_millis(process_start_time)
    command = command.strip()

    # Check if we should ignore this commannd or not.
    if "#ignore" in command:
        return

    context = UserContext(pid, pid_start_time, BH_USER_ID, BH_SYSTEM_ID)
    command = Command(command, path, context)
    rest_client.save_command(command)

@bashhub.command()
def setup():
    """Run bashhub user and system setup"""
    bashhub_setup.main()

@bashhub.command()
def update():
    """Update your bashhub installation"""
    url = 'http://bashhub.com/setup'
    response = requests.get(url, stream=True)
    filename = 'update-bashhub.sh'
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    subprocess.call("bash " + filename, shell=True)

@bashhub.group()
def util():
    """misc utils for the command line"""
    pass

@util.command()
@click.argument('date_string', type=str)
def parsedate(date_string):
    """date string to seconds since the unix epoch"""
    date = dateutil.parser.parse(date_string)
    unix_time = int(mktime(date.timetuple()))
    click.echo(unix_time)

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
