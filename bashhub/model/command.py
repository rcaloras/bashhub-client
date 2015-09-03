#!/usr/bin/python
from bson.objectid import ObjectId
from time import *
import jsonpickle
import sys
import uuid
from serializable import Serializable

class Command(Serializable):

    def __init__(self, command, path, uuid, username,
            system_name, session_id, created, id, exit_status = None):
        self.command = command
        self.path = path
        self.uuid = uuid
        self.exit_status = exit_status
        self.username = username
        self.system_name = system_name
        self.session_id = session_id
        self.created = created
        self.id = id

    # Optional fields not set by jsonpickle.
    exit_status = None

class RegisterUser(Serializable):
    def __init__(self, email, username, password, registration_code = ""):
        self.email = email
        self.username = username
        self.password = password
        self.registration_code = registration_code

class UserCredentials(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def to_JSON(self):
        return jsonpickle.encode(self)
