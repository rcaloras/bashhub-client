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


@cli.app.CommandLineApp
def bh(app):
    payload = {'userId' : '52364ac5b52d605f31a78c44', 'limit' : app.params.number}
    url = 'http://bashhub.com/command/last'
    #url = "http://localhost:9000/command"
    r = requests.get(url, params=payload)
    commandsJson = r.json()
    for command in commandsJson:
        minCommand = MinCommand.from_JSON(json.dumps(command))
        print minCommand

bh.add_param("-n", "--number", help="Number of previous commands",
            default=100, type=int)


if __name__ == "__main__":
    bh.run()
