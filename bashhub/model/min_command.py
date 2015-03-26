from bson.objectid import ObjectId
import jsonpickle
import json
import requests
from serializable import Serializable

class MinCommand(Serializable):

    def __init__(self, command, created):
        self.command = command
        self.created = created

    def __str__(self):
        return self.command.encode('utf8')


