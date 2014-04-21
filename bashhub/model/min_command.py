from bson.objectid import ObjectId
import jsonpickle
import json
import requests

class MinCommand(object):

    def __init__(self, command, created):
        self.command = command
        self.created = created

    def to_JSON(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_JSON(response):
        temp = json.loads(response)
        temp['py/object'] = 'bashhub.model.min_command.MinCommand'
        pickle = json.dumps(temp)
        return jsonpickle.decode(pickle)

    def __str__(self):
        return self.command


