#!/usr/bin/python
import json
import sys
import requests
from requests import ConnectionError
import cli.app
import os

from model import MinCommand
from bashhub_globals import *
import rest_client

@cli.app.CommandLineApp
def bh(app):
    """Parse command line arguments and call our REST API"""
    limit = app.params.number
    user_id = BH_USER_ID
    path = os.getcwd if app.params.directory else ''
    query = app.params.query
    system_id = BH_SYSTEM_ID if app.params.system else ''

    # Call our rest api to search for commands
    commands = rest_client.search(user_id, limit, path, query, system_id)
    print_commands(commands)

def print_commands(commands):
    for command in (commands):
       print command

bh.add_param("-n", "--number", help="Limit the number of previous commands. \
        Default is 100.", default=100, type=int)

bh.add_param("query", nargs='?', help="Like string to search for", \
        default="", type=str)

bh.add_param("-d", "--directory", help="Search for commands within this \
        directory.", default=False, action='store_true')

bh.add_param("-sys", "--system", help="Search for commands created on this \
        system.", default= False, action='store_true')

def main():
    try:
        bh.run()
    except Exception as e:
        print "Oops, look like an exception occured: " + str(e)

main()
