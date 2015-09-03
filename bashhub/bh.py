#!/usr/bin/python

from __future__ import print_function
import json
import sys
import requests
from requests import ConnectionError
import cli.app
import os
import io
import traceback

from model import MinCommand
from bashhub_globals import *
import rest_client
from i_search import InteractiveSearch

@cli.app.CommandLineApp
def bh(app):
    """Parse command line arguments and call our REST API"""
    limit = app.params.number
    user_id = BH_USER_ID
    query = app.params.query
    system_id = BH_SYSTEM_ID if app.params.system else None
    path = os.getcwd() if app.params.directory else None
    # By default show unique on the client.
    unique = not app.params.duplicates

    # If we're interactive, make sure we have a query
    if app.params.interactive and query == '':
        query = raw_input("(bashhub-i-search): ")

    # Call our rest api to search for commands
    commands = rest_client.search(
      user_id = user_id,
      limit = limit,
      path = path,
      query = query,
      system_id = system_id,
      unique = unique)

    if app.params.interactive:
        run_interactive(commands)
    else:
        print_commands(commands)

def print_commands(commands):
    for command in reversed(commands):
        print(command.command)

def run_interactive(commands):
    i_search = InteractiveSearch(commands, rest_client)
    i_search.run()
    # numpy bullshit since it doesn't return anything.
    # Consider submitting a patchset for it.
    command = i_search.return_value
    if command is not None:
        f = io.open(BH_HOME + '/response.bh','w+', encoding='utf-8')
        print(command.command, file=f)

bh.add_param("-n", "--number", help="Limit the number of previous commands. \
        Default is 100.", default=100, type=int)

bh.add_param("query", nargs='?', help="Like string to search for", \
        default="", type=str)

bh.add_param("-d", "--directory", help="Search for commands within this \
        directory.", default=False, action='store_true')

bh.add_param("-sys", "--system", help="Search for commands created on this \
        system.", default= False, action='store_true')

bh.add_param("-i", "--interactive", help="Use interactive search. Allows you \
        to select commands to run.", default= False, action='store_true')

bh.add_param("-dups", "--duplicates", help="Include duplicates", \
        default=False, action='store_true')

def main():
    try:
        bh.run()
    except Exception as e:
        print("Oops, look like an exception occured: " + str(e))
        print(traceback.format_exc())
        sys.exit(1)
    except KeyboardInterrupt:
        # To allow Ctrl+C (^C). Print a new line to drop the prompt.
        print()
        sys.exit()

main()
