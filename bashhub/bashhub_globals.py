"""
This file should be used for declaring any global variables that need to be
pulled in from environment variables or are just used across multiple files.
"""

import os

def get_global_from_env(env_var, default):
    default if env_var not in os.environ.keys() \
            else os.environ(env_var)


# Optional environment variable to configure for development
# export BH_URL='http://localhost:9000'
BH_URL = get_global_from_env('BH_URL', 'http://bashhub.com')

BH_USER_ID = get_global_from_env('BH_USER_ID', '')

BH_SYSTEM_ID = get_global_from_env('BH_SYSTEM_ID', '')

BH_HOME = "~/.bashhub/" if "HOME" not in os.environ.keys() \
        else os.environ["HOME"] + '/.bashhub'


