#!/usr/bin/python
from bson.objectid import ObjectId
from time import *
import jsonpickle
import json
import sys
import requests

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

class RegisterUser(object):
    def __init__(self, email, username, password, registration_code = ""):
        self.email = email
        self.username = username
        self.password = password
        self.registration_code = registration_code

    def to_JSON(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_JSON(json):
        return jsonpickle.decode(json)

class UserCredentials(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


    def to_JSON(self):
        return jsonpickle.encode(self)

class UserContext(object):
    def __init__(self, process_id, start_time, user_id, system_id):
        self.process_id = long(process_id)
        #self.start_time = mktime(strptime(start_time.strip(), "%c"))*1000
        self.start_time = start_time
        self.user_id = user_id
        self.system_id = system_id

    def to_JSON(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_JSON(json):
        return jsonpickle.decode(json)


