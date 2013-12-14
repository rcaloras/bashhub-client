"""
This file should be used for declaring any global variables that need to be
pulled in from environment variables or are just used across multiple files.
"""

import os

BH_URL = "http://bashhub.com"
BH_USER_ID = os.environ["BH_USER_ID"]
BH_SYSTEM_ID = os.environ["BH_SYSTEM_ID"]
