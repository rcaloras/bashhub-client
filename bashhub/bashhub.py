#!/usr/bin/python
import json
import sys
import requests
from requests import ConnectionError
import cli.app

from model import Command
from bashhub_globals import *


@cli.app.CommandLineApp
def bashhub(app):
    context = User_Context(long(args[4]), args[5], args[2], args[3])
    command = Command(args[1], args[6], context)
    url = BH_URL + "/command"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        r = requests.post(url, data=command.to_JSON(), headers=headers)
        #print command.to_JSON()
    except ConnectionError as error:
        pass

bashhub.add_param("command", help="command to record", type=str)
bashhub.add_param("path", help="the path the command was executed in", type=str)
bashhub.add_param("user_id", help="bashhub user id", type=str)
bashhub.add_param("system_id", help="id of this system", type=str)
bashhub.add_param("pid_start_time", help="start time of the parent pid", type=long)
bashhub.add_param("parent_pid", help="the pid of the shell this command was executed in", type=long)

def main():
    try:
        bashhub.run()
    except Exception as e:
        print "Oops, look like an exception occured: " + str(e)

main()
