#!/usr/bin/python
from bson.objectid import ObjectId
from time import *
import jsonpickle
import json
import sys
import requests
import getpass
import traceback
import uuid
from model import *
from model import System
from bashhub_globals import *
import requests
from requests import ConnectionError
from requests import HTTPError


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def register_new_user(register_user):
    url = BH_URL + "/user/register"
    headers = {'content-type': 'application/json'}
    try:
        response = requests.post(url, data=register_user.to_JSON(), headers=headers)
        response.raise_for_status()
        return response.json()

    except ConnectionError as error:
        print "Looks like there's a connection error. Please try again later"
    except HTTPError as error:
        if response.status_code == 409:
            print response.text
        else:
            print error
            print "Please try again..."
    return None

def register_new_system(register_system):
    url = BH_URL + "/system/register"
    headers = {'content-type': 'application/json'}
    try:
        print register_system.to_JSON()
        response = requests.post(url, data=register_system.to_JSON(), headers=headers)
        response.raise_for_status()
        return response.json()

    except ConnectionError as error:
        print "Looks like there's a connection error. Please try again later"
    except HTTPError as error:
        if response.status_code == 409:
            print response.text
        else:
            print error
            print "Please try again..."
    return None

def check_credentials(user_credentials):
    url = BH_URL + "/user/credentials"
    headers = {'content-type': 'application/json'}
    try:
        response = requests.post(url, data=user_credentials.to_JSON(), headers=headers)
        response.raise_for_status()
        return response.json()

    except ConnectionError as error:
        print "Looks like there's a connection error. Please try again later"
    except HTTPError as error:
        if response.status_code == 409:
            print response.text
        elif response.status_code == 400:
            print "Bad password. Try again."
        else:
            print error
            print "Please try again..."
    return None

def get_new_user_information():
    email = raw_input("What's your email? ")
    username = raw_input("What username would you like? ")
    password = getpass.getpass("What password? ")
    print "\nEmail: " + email + " Username: " + username
    all_good = query_yes_no("Are these correct?")
    if all_good:
        return RegisterUser(email, username, password)
    else:
        return get_new_user_information()

def get_existing_user_information(attempts=0):
    if attempts == 4:
        print "Too many bad attempts"
        return None

    print "Please enter your bashhub credentials"
    username = raw_input("Username: ")
    password = getpass.getpass("Password: ")
    credentials = UserCredentials(username, password)

    url = BH_URL + "/user/auth"
    headers = {'content-type': 'application/json'}
    try:
        response = requests.post(url, data=credentials.to_JSON(), headers=headers)
        response.raise_for_status()
        return response.json()

    except ConnectionError as error:
        print "Looks like there's a connection error. Please try again later"
    except HTTPError as error:
        if response.status_code == 409:
            print response.text
            return get_existing_user_information(attempts+1)
        elif response.status_code == 400:
            print "Bad password. Try again."
            return get_existing_user_information(attempts+1)
        else:
            print error
            print "Please try again..."
            return get_existing_user_information(attempts+1)

def get_system_information(mac, user_id):

    url = BH_URL + '/system'
    payload = {'userId' : user_id, 'mac' : mac}
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        system_json = json.dumps(response.json())
        print "System_Json"
        print system_json
        return System.from_JSON(system_json)
    except ConnectionError as error:
        print "Looks like there's a connection error. Please try again later"
    except HTTPError as error:
        return None

def handle_system_information(user_id):
    mac = uuid.getnode()
    system = get_system_information(mac, user_id)

    # If this system is already registered
    if system is not None:
        print("Looks like this box is already registered as " + system.name)
        return system.id
    else:
        name = raw_input("What do you want to call this system? " + \
            "For example Work Laptop, Home, File Server, ect.: ")

        system = RegisterSystem(name, mac, user_id)
        system_id = register_new_system(system)
        return  system_id


def write_config_file(user_id, system_id):
    exists = os.path.exists(BH_HOME)
    if exists:
        config_file = open(BH_HOME + '/.config', 'w')
        config_file.write("export BH_USER_ID=\"" + user_id + "\"\n")
        config_file.write("export BH_SYSTEM_ID=\"" + system_id + "\"\n")
    else:
        print "Couldn't find bashhub home directory. Sorry."


def main():
    try:
        print "Welcome to bashhub setup!"
        is_new_user = query_yes_no("Are you a new user?")
        user_id = None
        if is_new_user:
            register_user = get_new_user_information()
            user_id = register_new_user(register_user)
        else:
            user_id = get_existing_user_information()

        if user_id == None:
            print "Sorry looks like getting your info failed.\
                    Exiting..."
            sys.exit(0)

        system_id = handle_system_information(user_id)
        print "(user_id, system_id) = (" + user_id + ", " + system_id + ")"
        write_config_file(user_id, system_id)
        sys.exit(0)

    except Exception, err:
        sys.stderr.write('Setup Error:\n%s\n' % str(err))
        traceback.print_exc()
        sys.exit(1)

if __name__== "__main__":
    main()
