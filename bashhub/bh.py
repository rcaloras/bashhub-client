#!/usr/bin/python
from bson.objectid import ObjectId
from time import *
import jsonpickle
import json
import sys
import requests
from requests import ConnectionError
import cli.app

from model import MinCommand
from bashhub_globals import *


@cli.app.CommandLineApp
def bh(app):
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

#bh.add_param("query", help="query in regular expression format",
#            default="", type=str)


bh.add_param("-n", "--number", help="Number of previous commands",
            default=100, type=int)


def main():
    try:
        bh.run()
    except Exception as e:
        print "Oops, look like an exception occured: " + str(e)
