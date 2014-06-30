import jsonpickle
import json
import requests
from serializable import Serializable

class System(Serializable):

    def __init__(self, name, mac, id, created, updated):
        self.name = name
        self.mac = mac
        self.id = id
        self.created = created
        self.updated = updated

    def __str__(self):
        return self.name + " " + self.id


