#!/usr/bin/python
import json
import sys
import requests
from requests import ConnectionError
import cli.app
import os

from model import MinCommand
from bashhub_globals import *


@cli.app.CommandLineApp
def bh(app):
    limit = app.params.number
    payload = {'userId' : BH_USER_ID, 'limit' : app.params.number}
    if app.params.directory:
        payload["path"] = os.getcwd()

    if app.params.query:
        payload["command"] = app.params.query

    if app.params.system:
        payload["systemId"] = BH_SYSTEM_ID

    url = BH_URL + "/command/search"
    try:
        r = requests.get(url, params=payload)
        print_commands(reversed(r.json()))

    except ConnectionError as error:
        print "Sorry, looks like there's a connection error. Please try again later"


def print_commands(commands_json):
    for command in (commands_json):
       min_command = MinCommand.from_JSON(json.dumps(command))
       print min_command

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
