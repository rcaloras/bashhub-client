#!/usr/bin/python
from bson.objectid import ObjectId
from time import *
import jsonpickle
import json
import sys
import requests
from requests import *

class Command(object):
    def __init__(self, command, path, context):
        self.id = ObjectId().__str__()
        self.command = command
        self.created = time()*1000
        self.context = context
        self.path = path

    def to_JSON(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_JSON(json):
        return jsonpickle.decode(json)

class User_Context(object):
    def __init__(self, process_id, start_time, user_id, system_id):
        self.process_id = long(process_id)
        self.start_time = mktime(strptime(start_time.strip(), "%c"))
        self.user_id = user_id
        self.system_id = system_id

    def to_JSON(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_JSON(json):
        return jsonpickle.decode(json)


if __name__== "__main__":

    if len(sys.argv) > 1:
        args = sys.argv
        context = User_Context(long(args[4]), args[5], args[2], args[3])
        command = Command(args[1], args[6], context)
        url = "http://bashhub.com/command"
        #url = "http://localhost:9000/command"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            r = requests.post(url, data=command.to_JSON(), headers=headers)
            #print command.to_JSON()
        except ConnectionError as error:
            pass
