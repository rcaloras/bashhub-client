#!/usr/bin/python
import sys
from requests import ConnectionError
import requests
from bashhub_globals import *
sys.path.insert(0, 'model')
from Command import *

if __name__== "__main__":
    if len(sys.argv) > 1:
        args = sys.argv
        context = User_Context(long(args[4]), args[5], args[2], args[3])
        command = Command(args[1], args[6], context)
        url = BH_URL + "/command"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            r = requests.post(url, data=command.to_JSON(), headers=headers)
            #print command.to_JSON()
        except ConnectionError as error:
            pass
