#!/usr/bin/python
from __future__ import print_function
from time import *
import click
import traceback
import dateutil.parser
import sys
import os
import io

from .model import CommandForm
from . import rest_client
from . import bashhub_setup
from . import bashhub_globals
from .bashhub_globals import BH_FILTER, BH_HOME, BH_SAVE_COMMANDS
from .bashhub_globals import write_to_config_file
from .version import version_str
import shutil
import requests
import subprocess
from . import shell_utils
import re
from .view.status import *

from builtins import str as text


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(version_str)
    ctx.exit()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-V',
              '--version',
              default=False,
              is_flag=True,
              callback=print_version,
              help='Display version',
              expose_value=False,
              is_eager=True)
def bashhub():
    """Bashhub command line client"""
    pass


@bashhub.command()
def version():
    """Display version"""
    click.echo(version_str)


@bashhub.command()
@click.option("-g",
              "--global",
              "is_global",
              default=False,
              is_flag=True,
              help="Turn off saving commands for all sessions.")
def off(is_global):
    """Turn off saving commands to Bashhub. Applies for this current session."""
    if is_global:
        write_to_config_file('save_commands', 'False')
    else:
        f = io.open(BH_HOME + '/script.bh', 'w+', encoding='utf-8')
        print(text("export BH_SAVE_COMMANDS='False'"), file=f)


@bashhub.command()
@click.option('-l',
              "--local",
              help="Turn on saving commands for only this session.",
              is_flag=True)
def on(local):
    """Turn on saving commands to Bashhub. Applies globally."""
    f = io.open(BH_HOME + '/script.bh', 'w+', encoding='utf-8')

    if local:
        print(text("export BH_SAVE_COMMANDS='True'"), file=f)
    else:
        print(text("unset BH_SAVE_COMMANDS"), file=f)
        write_to_config_file('save_commands', 'True')


@bashhub.command()
@click.argument('command', type=str)
@click.argument('path', type=click.Path(exists=True))
@click.argument('pid', type=int)
@click.argument('process_start_time', type=int)
@click.argument('exit_status', type=int)
def save(command, path, pid, process_start_time, exit_status):
    """Save a command to Bashhub"""
    pid_start_time = unix_time_to_epoc_millis(process_start_time)
    command = command.strip()

    # Check if we have commands saving turned on
    if not bashhub_globals.BH_SAVE_COMMANDS:
        return

    # Check if we should ignore this command.
    if "#ignore" in command:
        return

    # Check if we should filter this command.
    bh_filter = bashhub_globals.BH_FILTER
    if bh_filter and re.findall(bh_filter, command):
        return

    # Check that we have an auth token.
    if bashhub_globals.BH_AUTH() == "":
        print("No auth token found. Run 'bashhub setup' to login.")
        return

    command = CommandForm(command, path, exit_status, pid, pid_start_time)
    rest_client.save_command(command)


@bashhub.command()
def setup():
    """Run Bashhub user and system setup"""
    bashhub_setup.main()


@bashhub.command()
def status():
    """Stats for this session and user"""
    # Get our user and session information from our context
    (ppid, start_time) = shell_utils.get_session_information()
    status_view = rest_client.get_status_view(ppid, start_time)
    if status_view:
        click.echo(build_status_view(status_view))


@bashhub.command()
@click.pass_context
def help(ctx):
    """Show this message and exit"""
    click.echo(ctx.parent.get_help())

# Dynamic help text containing the BH_FILTER variable.
filtered_text = "BH_FILTER={0}".format(
    BH_FILTER) if BH_FILTER else "BH_FILTER \
is unset."

filter_help_text = """Check if a command is filtered from bashhub. Filtering
is configured via a regex exported as BH_FILTER.
\n
{0}""".format(filtered_text)


@bashhub.command(help=filter_help_text)
@click.argument('command', type=str)
@click.option('-r',
              '--regex',
              default=BH_FILTER,
              help='Regex to filter against')
def filter(command, regex):

    # Check if the regex we receive is valid
    if not bashhub_globals.is_valid_regex(regex):
        click.secho("Regex {0} is invalid".format(regex), fg='red')
        return

    v = re.findall(regex, command)
    click.echo(filtered_text)
    if v and regex:
        matched = [str(s) for s in set(v)]
        output = click.style("{0} \nIs Filtered. Matched ".format(command),
                             fg='yellow') + click.style(
                                 str(matched), fg='red')
        click.echo(output)
    else:
        click.echo("{0} \nIs Unfiltered".format(command))


@bashhub.command()
@click.argument('version', type=str, default='')
def update(version):
    """Update your Bashhub installation"""

    if version != '':
        github = "https://github.com/rcaloras/bashhub-client/archive/{0}.tar.gz".format(
            version)
        response = requests.get(github)
        if response.status_code is not 200:
            click.echo("Invalid version number {0}".format(version))
            sys.exit(1)

    query_param = '?version={0}'.format(version) if version else ''
    url = 'https://bashhub.com/setup' + query_param
    response = requests.get(url, stream=True)
    filename = 'update-bashhub.sh'
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    shell_command = "bash -e {0} {1}".format(filename, version)
    subprocess.call(shell_command, shell=True)
    os.remove(filename)


@bashhub.group()
def util():
    """Misc utils used by Bashhub"""
    pass


@util.command()
def update_system_info():
    """Updates system info for Bashhub"""
    result = bashhub_setup.update_system_info()
    # Exit code based on if our update call was successful
    sys.exit(0) if result != None else sys.exit(1)


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
    return int(unix_time) * 1000


def main():
    try:
        bashhub()
    except Exception as e:
        formatted = traceback.format_exc(e)
        click.echo("Oops, looks like an exception occured: " + str(e))
        sys.exit(1)
