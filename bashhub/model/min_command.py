import json
import requests
from .serializable import Serializable

# For unicode support on __str__
from future.utils import python_2_unicode_compatible


@python_2_unicode_compatible
class MinCommand(Serializable):
    def __init__(self, command, created, uuid):
        self.command = command
        self.created = created
        self.uuid = uuid

    def __str__(self):
        return self.command
