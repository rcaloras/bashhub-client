"""
This file should be used for declaring any global variables that need to be
pulled in from environment variables or are just used across multiple files.
"""

import os
import re

# Optional environment variable to configure for development
# export BH_URL='http://localhost:9000'
BH_URL = os.getenv('BH_URL', 'https://bashhub.com')

BH_USER_ID = os.getenv('BH_USER_ID', '')

BH_SYSTEM_ID = os.getenv('BH_SYSTEM_ID', '')

BH_HOME = '~/.bashhub' if 'HOME' not in os.environ.keys() \
        else os.environ['HOME'] + '/.bashhub'

def is_valid_regex(regex):
    try:
        re.compile(regex)
        return True
    except re.error:
        return False

BH_FILTER = os.getenv('BH_FILTER', '') if is_valid_regex(os.getenv('BH_FILTER', '')) \
        else '__invalid__'
