#!/usr/bin/python
from __future__ import annotations

import getpass
import socket
import sys
import traceback
import uuid
from typing import Callable

from . import rest_client
from .bashhub_globals import *
from .model import *
from .validation import validate_email, validate_password, validate_username
from .version import __version__


def query_yes_no(question: str, default: str = "yes") -> bool:
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
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


def prompt_until_valid(
    prompt: str,
    validator: Callable[[str], str | None],
    secret: bool = False,
) -> str:
    """Prompt the user until validator() returns None. Re-prompts with the
    error message on failure."""
    while True:
        value = getpass.getpass(prompt) if secret else input(prompt)
        error = validator(value)
        if error is None:
            return value
        print(error)


def prompt_password_with_confirmation() -> str:
    """Prompt for a password, validate it, then require a matching
    confirmation. Re-prompts from the start if the confirmation doesn't
    match."""
    while True:
        password = prompt_until_valid(
            "What password? ", validate_password, secret=True)
        confirm = getpass.getpass("Confirm password: ")
        if password == confirm:
            return password
        print("Passwords did not match. Please try again.")


def get_new_user_information() -> RegisterUser:
    email = prompt_until_valid("What's your email? ", validate_email)
    username = prompt_until_valid(
        "What username would you like? ", validate_username)
    password = prompt_password_with_confirmation()
    print("\nEmail: " + email + " Username: " + username)
    all_good = query_yes_no("Are these correct?")

    if all_good:
        return RegisterUser(email, username, password)
    else:
        return get_new_user_information()


def get_user_information_and_login(
    username: str | None = None,
    password: str | None = None,
    attempts: int = 0,
) -> tuple[str | None, str | None, str | None]:
    if attempts == 4:
        print("Too many bad attempts.")
        return (None, None, None)

    # Only collect user information if we don't already have it
    # i.e. if we didn't just register a new user.
    if username is None and password is None:
        print("Please enter your bashhub credentials")
        username = input("Username: ")
        password = getpass.getpass("Password: ")

    # login once we have all of our information
    if username is None or password is None:
        return (None, None, None)
    access_token = rest_client.login_user(LoginForm(username, password))

    # Package our result to include our credentials to later login our system.
    if access_token:
        return (username, password, access_token)
    return get_user_information_and_login(attempts=attempts + 1) or (
        None, None, None)


def get_mac_address() -> str:
    """Get the mac address for our system as a fingerprint. If we can't
    get the mac, use the hash of our hostname as a subtitute"""

    mac_int = uuid.getnode()
    # check if getnode fails
    if (mac_int >> 40) & 1:
        hostname = socket.gethostname()
        print("warning: cannot find MAC. Using hostname (%s) to identify system" % hostname)
        return hostname
    return str(mac_int)


# Update our hostname incase it changed.
def update_system_info() -> int | None:
    mac = get_mac_address()
    hostname = socket.gethostname()
    patch = SystemPatch(hostname=hostname, client_version=__version__)
    return rest_client.patch_system(patch, mac)


def handle_system_information(
    username: str,
    password: str,
    attempts: int = 0,
) -> tuple[str | None, str | None]:

    mac = get_mac_address()
    system = rest_client.get_system_information(mac)
    system_name: str | None = None
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
            if attempts < 3:
                print("Looks like registering your system failed. Let's retry.")
                return handle_system_information(username, password, attempts + 1)
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


def main() -> None:
    try:

        ascii_art = r"""
          ____            _     _           _
         |  _ \          | |   | |         | |
         | |_) | __ _ ___| |__ | |__  _   _| |__   ___ ___  _ __ ___
         |  _ < / _` / __| '_ \| '_ \| | | | '_ \ / __/ _ \| '_ ` _  \
         | |_) | (_| \__ \ | | | | | | |_| | |_) | (_| (_) | | | | | |
         |____/ \__,_|___/_| |_|_| |_|\__,_|_.__(_)___\___/|_| |_| |_|

        """

        print(ascii_art)
        print("Welcome to bashhub setup!")
        is_new_user = query_yes_no("Are you a new user?")

        # Initialize variaous Credentials for logging in.
        username: str | None = None
        password: str | None = None
        access_token: str | None = None

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
        if access_token is None:
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

        if username is None or password is None:
            print("Sorry looks like getting your credentials failed. Exiting...")
            sys.exit(1)
        (access_token, system_name) = handle_system_information(username,
                                                                password)

        if access_token is None or system_name is None:
            print("Sorry looks like getting your access_token or system_name failed.\
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
