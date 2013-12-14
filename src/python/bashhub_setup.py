#!/usr/bin/python
from bson.objectid import ObjectId
from time import *
import jsonpickle
import json
import sys
import requests
import getpass
sys.path.insert(0, 'model')
from Command import *
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
        response = requests.put(url, data=register_user.to_JSON(), headers=headers)
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
    return "error"

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

if __name__== "__main__":
    print "Welcome to bashhub setup!"
    is_new_user = query_yes_no("Are you a new user?")
    if is_new_user:
        ask_user = True
        register_user = get_new_user_information()
        result = register_new_user(register_user)
        print result
    else:
        print "Please enter your bashhub credentials"
        username = raw_input("Username: ")
        password = getpass.getpass("Password: ")
        credentials = UserCredentials(username, password)
        print credentials.to_JSON()

