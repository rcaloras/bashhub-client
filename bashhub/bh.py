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
    directory = os.getcwd() if app.params.directory else ""
    is_interactive = app.params.interactive
    payload = {'userId' : BH_USER_ID, 'limit' : app.params.number}
    url = BH_URL + "/command/last"
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

bh.add_param("-d", "--directory", help="Search for commands within this \
        directory.", default=False, type=bool)

bh.add_param("-i", "--interactive", help="Use interactive history search. \
        Defaults to false", default=False, type=bool)

bh.add_param("query", help="String to search through history for",
            default="", type=str)

def main():
    try:
        bh.run()
    except Exception as e:
        print "Oops, look like an exception occured: " + str(e)

main()
