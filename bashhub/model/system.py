from bson.objectid import ObjectId
import jsonpickle
import json
import requests

class System(object):

    def __init__(self, name, mac, user_id, id, created, updated):
        self.name = name
        self.mac = mac
        self.user_id = user_id
        self.id = id
        self.created = created
        self.updated = updated

    def to_JSON(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_JSON(response):
        temp = json.loads(response)
        temp['py/object'] = 'bashhub.model.system.System'
        temp['user_id'] = temp['userId']
        del temp['userId']
        pickle = json.dumps(temp)
        return jsonpickle.decode(pickle)

    def __str__(self):
        return self.name + " " + self.uuid


