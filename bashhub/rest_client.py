#!/usr/bin/python
import json
import sys
import requests
from requests import ConnectionError
import os

from model import MinCommand
from bashhub_globals import *

def search(user_id, limit=100, path='', query='', system_id='',
        session_name=''):

    payload = {'userId' : user_id, 'limit' : limit }

    if path:
        payload["path"] = os.getcwd()

    if query:
        payload["query"] = query

    if system_id:
        payload["systemId"] = BH_SYSTEM_ID

    url = BH_URL + "/command/v1/search"

    try:
        r = requests.get(url, params=payload)
        return MinCommand.from_JSON_list(r.json())

    except ConnectionError as error:
        print "Sorry, looks like there's a connection error. Please try again later"
        return []


