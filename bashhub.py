#!/usr/bin/python
from bson.objectid import ObjectId
from time import time
import jsonpickle
import json
import sys
import requests
from requests import *

class Command:
    def __init__(self, command):
        self.id = ObjectId().__str__()
        self.command = command
        self.created = time()*1000

    def to_JSON(self):
        return jsonpickle.encode(self)


if __name__== "__main__":

    if len(sys.argv) > 1:
        command = Command(sys.argv[1])
        url = "http://bashhub.com/command"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            r = requests.post(url, data=command.to_JSON(), headers=headers)
        except ConnectionError as error:
            pass
