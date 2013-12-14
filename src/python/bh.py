#!/usr/bin/python
from bson.objectid import ObjectId
from time import *
import jsonpickle
import json
import sys
import requests
import cli.app
sys.path.insert(0, 'model')
from Command import *
from bashhub_globals import *


@cli.app.CommandLineApp
def bh(app):
    payload = {'userId' : BH_USER_ID, 'limit' : app.params.number}
    url = BH_URL + "/command/last"
    r = requests.get(url, params=payload)
    commandsJson = r.json()
    for command in reversed(commandsJson):
        minCommand = MinCommand.from_JSON(json.dumps(command))
        print minCommand


#bh.add_param("query", help="query in regular expression format",
#            default="", type=str)


bh.add_param("-n", "--number", help="Number of previous commands",
            default=100, type=int)


if __name__ == "__main__":
    bh.run()
