from bson.objectid import ObjectId
import jsonpickle
import json
import requests
from serializable import Serializable


class MinCommand(Serializable):
    def __init__(self, command, created, uuid):
        self.command = command
        self.created = created
        self.created = uuid

    def __str__(self):
        return self.command.encode('utf8')
