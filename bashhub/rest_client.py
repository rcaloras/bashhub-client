#!/usr/bin/python
import json
import sys
import requests
from requests import ConnectionError
import os

from model import MinCommand
from model import StatusView
from model import Command
from bashhub_globals import *
from version import __version__
from requests import ConnectionError
from requests import HTTPError

# Build our user agent string
user_agent = 'bashhub/%s' % __version__

base_headers = {
        'User-Agent' : user_agent,
        'X-Bashhub-version' : __version__
}


json_headers = dict(
        { 'content-type': 'application/json',
          'Accept': 'text/plain'
        }, **base_headers)

def register_user(register_user):

    url = BH_URL + "/user/v1/register"
    try:
        response = requests.post(url, data=register_user.to_JSON(),
                headers=json_headers)
        response.raise_for_status()
        return response.json()

    except ConnectionError as error:
        print("Looks like there's a connection error. Please try again later")
    except HTTPError as error:
        if response.status_code == 409:
            print(response.text)
        else:
            print(error)
            print("Please try again...")
    return None

def get_command(uuid):

    url = BH_URL + "/api/v1/command/{0}".format(uuid)

    try:
        response = requests.get(url, headers=json_headers)
        response.raise_for_status()
        json_command = json.dumps(response.json())
        return Command.from_JSON(json_command)

    except ConnectionError as error:
        print("Looks like there's a connection error. Please try again later")
    except HTTPError as error:
            print(error)
            print("Please try again...")

    return None


def authenticate_user(credentials):

    url = BH_URL + "/user/v1/auth"

    try:
        response = requests.post(url, data=credentials.to_JSON(),
                headers=json_headers)

        response.raise_for_status()
        return response.json()

    except ConnectionError as error:
        print("Looks like there's a connection error. Please try again later")
        return None
    except HTTPError as error:
        if response.status_code == 409:
            print(response.text)
        elif response.status_code == 400:
            print("Bad password. Try again.")
        else:
            print(error)
            print("Please try again...")
        return None

def patch_system(system_patch, system_id=BH_SYSTEM_ID):

    url = BH_URL + "/api/v1/system/{0}".format(system_id)

    try:
        r = requests.patch(url, data=system_patch.to_JSON(), headers=json_headers)
        r.raise_for_status()
        r.status_code
    except Exception as error:
        print("Sorry, looks likes an error occured " + str(error))
        None

def search(user_id=BH_USER_ID, limit=100, path=None, query=None,
        system_id=None, unique=False):

    payload = { 'userId' : user_id,
                'limit' : limit,
                # API Needs booleans in lower case
                'unique' : str(unique).lower() }
    if path:
        payload["path"] = path

    if query:
        payload["query"] = query

    if system_id:
        payload["systemId"] = system_id

    url = BH_URL + "/api/v1/command/search"

    try:
        r = requests.get(url, params=payload, headers=base_headers)
        return MinCommand.from_JSON_list(r.json())

    except ConnectionError as error:
        print "Sorry, looks like there's a connection error. Please try again later"
        return []

def save_command(command):
    url = BH_URL + "/api/v1/command"

    try:
        r = requests.post(url, data=command.to_JSON(), headers=json_headers)
    except ConnectionError as error:
        print "Sorry, looks like there's a connection error"
        pass

def get_status_view(user_context):
    url = BH_URL + "/client-view/v2/status"

    payload = { 'userId' : user_context.user_id,
                'systemId' : user_context.system_id,
                'processId' : user_context.process_id,
                'startTime' : user_context.start_time  }
    try:
        r = requests.get(url, params=payload, headers=base_headers)
        status_view_json = json.dumps(r.json())
        return StatusView.from_JSON(statusViewJson)
    except Exception as error:
        print("Sorry, looks like there's a connection error: " + str(error))
        return None

