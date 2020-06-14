import jsonpickle
import json
import requests
from .serializable import Serializable


class System(Serializable):
    def __init__(self, name, mac, id, created, updated, hostname,
                 client_version):
        self.name = name
        self.mac = mac
        self.id = id
        self.created = created
        self.updated = updated
        self.hostname = hostname
        self.client_version = client_version

    def __str__(self):
        return self.name + " " + self.id


class RegisterSystem(Serializable):
    def __init__(self, name, mac, hostname, client_version):
        self.name = name
        self.mac = mac
        self.hostname = hostname
        self.client_version = client_version


class SystemPatch(Serializable):
    def __init__(self,
                 name=None,
                 mac=None,
                 hostname=None,
                 client_version=None):
        self.name = name
        self.mac = mac
        self.hostname = hostname
        self.client_version = client_version

    def __str__(self):
        return self.name + " " + self.mac
