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
import stat
import socket
from . import rest_client
from .version import __version__
from .model import *
from .bashhub_globals import *
import requests
from requests import ConnectionError
from requests import HTTPError
import collections
from builtins import input

# Support for Python 2 and 3
try:
    import configparser
    from configparser import NoSectionError, NoOptionError
except ImportError:
    import ConfigParser as configparser


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
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
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_new_user_information():
    email = input("What's your email? ")
    username = input("What username would you like? ")
    password = getpass.getpass("What password? ")
    print("\nEmail: " + email + " Username: " + username)
    all_good = query_yes_no("Are these correct?")

    if all_good:
        return RegisterUser(email, username, password)
    else:
        return get_new_user_information()


def get_user_information_and_login(username=None, password=None, attempts=0):
    if attempts == 4:
        print("Too many bad attempts.")
        return None

    # Only collect user information if we don't already have it
    # i.e. if we didn't just register a new user.
    if username == None and password == None:
        print("Please enter your bashhub credentials")
        username = input("Username: ")
        password = getpass.getpass("Password: ")

    # login once we have all of our information
    access_token = rest_client.login_user(LoginForm(username, password))

    # Package our result to include our credentials to later login our system.
    if access_token:
        result = (username, password, access_token)
    else:
        result = get_user_information_and_login(attempts=attempts + 1) or (
            None, None, None)

    return result


# Update our hostname incase it changed.
def update_system_info():
    mac = uuid.getnode().__str__()
    hostname = socket.gethostname()
    patch = SystemPatch(hostname=hostname, client_version=__version__)
    return rest_client.patch_system(patch, mac)


def handle_system_information(username, password):

    mac = uuid.getnode().__str__()
    system = rest_client.get_system_information(mac)
    system_name = None
    # Register a new System if this one isn't recognized
    if system is None:
        hostname = socket.gethostname()
        name_input = input("What do you want to call this system? " +
                               "For example Home, File Server, ect. [%s]: " %
                               hostname)

        name = name_input or hostname
        system_name = rest_client.register_system(RegisterSystem(
            name, mac, hostname, __version__))
        if system_name:
            print("Registered a new system " + name)
        else:
            return (None, None)

    # Login with this new system
    access_token = rest_client.login_user(LoginForm(username, password, mac))

    if access_token is None:
        print("Failed to login with system.")
        return (None, None)

    # If this system is already registered
    if system is not None:
        system_name = system.name
        print("Welcome back! Looks like this box is already registered as " +
              system.name + ".")

    return (access_token, system_name)


def main():
    try:

        ascii_art = """\
          ____            _     _           _
         |  _ \          | |   | |         | |
         | |_) | __ _ ___| |__ | |__  _   _| |__   ___ ___  _ __ ___
         |  _ < / _` / __| '_ \| '_ \| | | | '_ \ / __/ _ \| '_ ` _  \\
         | |_) | (_| \__ \ | | | | | | |_| | |_) | (_| (_) | | | | | |
         |____/ \__,_|___/_| |_|_| |_|\__,_|_.__(_)___\___/|_| |_| |_|

        """

        print(ascii_art)
        print("Welcome to bashhub setup!")
        is_new_user = query_yes_no("Are you a new user?")

        # Initialize variaous Credentials for logging in.
        username = None
        password = None
        access_token = None

        # If this is a new user walk them through the registration flow
        if is_new_user:
            register_user = get_new_user_information()
            register_result = rest_client.register_user(register_user)
            if register_result:
                print("Registered new user {0}\n".format(
                    register_user.username))
                # Set our credentials to login later
                username = register_user.username
                password = register_user.password
            else:
                print("Sorry, registering a new user failed.")
                print("You can rerun setup using 'bashhub setup' in a new "
                      "terminal window.\n")
                sys.exit(0)

        (username, password, access_token) = get_user_information_and_login(
            username, password)
        if access_token == None:
            print("\nSorry looks like logging in failed.")
            print("If you forgot your password please reset it. "
                  "https://bashhub.com/password-reset")
            print("You can rerun setup using 'bashhub setup' in a new "
                  "terminal window.\n")
            sys.exit(0)

        # write out our user scoped access token
        config_write_result = write_to_config_file("access_token",
                                                   access_token)
        if not config_write_result:
            print("Writing your config file failed.")
            sys.exit(1)

        (access_token, system_name) = handle_system_information(username,
                                                                password)

        if access_token == None:
            print("Sorry looks like getting your info failed.\
                    Exiting...")
            sys.exit(0)

        # write out our system scoped token and the system name
        write_to_config_file("access_token", access_token)
        write_to_config_file("system_name", system_name)
        update_system_info()

        sys.exit(0)

    except Exception as err:
        sys.stderr.write('Setup Error:\n%s\n' % str(err))
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        # To allow Ctrl+C (^C). Print a new line to drop the prompt.
        print("")
        sys.exit()


if __name__ == "__main__":
    main()
