#!/usr/bin/python

import click
import sys
import io
import os
import traceback
import datetime
from builtins import input
from .bashhub_globals import *
from . import rest_client
from .i_search import InteractiveSearch
from .version import version_str
from builtins import str as text

@click.command()
@click.argument('query', type=str, default='')
@click.option('-n', '--number', default=None, help='Limit the number of previous commands. Default is 100.', type=int)
@click.option("-ses",
             "--session",
             help="Filter by specific session id. Default is None.",
             default=None,
             type=str)
@click.option("-d",
             "--directory",
             help="Search for commands within this directory.",
             default=False,
             is_flag=True)
@click.option("-sys",
             "--system",
             help="Search for commands created on this system.",
             default=False,
             is_flag=True)
@click.option("-i",
    "--interactive",
    help="Use interactive search. Allows you to select commands to run.",
    default=False,
    is_flag=True)
@click.option("-dups",
             "--duplicates",
             help="Include duplicates",
             default=False,
             is_flag=True)
@click.option("-t",
             "--timestamps",
             help="Include timestamps",
             default=False,
             is_flag=True)
@click.option("-V",
             "--version",
             help="Print version information",
             default=False,
             is_flag=True)
def bh(query, number, session, directory, system, interactive, duplicates, timestamps, version):
    """Bashhhub Search

    QUERY - Like string to search for
    """
    limit = number
    system_name = BH_SYSTEM_NAME if system else None
    path = os.getcwd() if directory else None
    session_id = session

    # By default show unique on the client.
    unique = not duplicates

    use_timestamps = timestamps

    # If we're interactive, make sure we have a query
    if interactive and query == '':
        query = input("(bashhub-i-search): ")

    if version and query == '':
        print(version_str)
        sys.exit()

    # Call our rest api to search for commands
    commands = rest_client.search(limit=limit,
                                  path=path,
                                  query=query,
                                  system_name=system_name,
                                  unique=unique,
                                  session_id=session_id)

    if interactive:
        run_interactive(commands)
    else:
        print_commands(commands, use_timestamps)


def print_commands(commands, use_timestamps):
    for command in reversed(commands):
        if use_timestamps:
            timestamp = unix_milliseconds_timestamp_to_datetime(command.created)
            print('%s\t%s' % (timestamp, command.command))
        else:
            print(command.command)


def run_interactive(commands):
    i_search = InteractiveSearch(commands, rest_client)
    i_search.run()
    # numpy bullshit since it doesn't return anything.
    # Consider submitting a patchset for it.
    command = i_search.return_value
    if command is not None:
        f = io.open(BH_HOME + '/response.bh', 'w+', encoding='utf-8')
        print(text(command.command), file=f)

def unix_milliseconds_timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp) / 1000) \
        .strftime('%Y-%m-%d %H:%M:%S')

def main():
    try:
        bh()
    except Exception as e:
        if BH_DEBUG:
            traceback.print_exc()
        click.echo("Oops, look like an exception occured: " + str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        # To allow Ctrl+C (^C). Print a new line to drop the prompt.
        click.echo()
        sys.exit()

main()
