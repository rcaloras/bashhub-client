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

class MinCommand(object):

    def __init__(self, command, created):
        self.command = command
        self.created = created

    def to_JSON(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_JSON(response):
        temp = json.loads(response)
        temp['py/object'] = 'Command.MinCommand'
        pickle = json.dumps(temp)
        return jsonpickle.decode(pickle)

    def __str__(self):
        return self.command

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


