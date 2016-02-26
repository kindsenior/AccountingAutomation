#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import httplib2

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
# SCOPES = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/gmail.readonly'
SCOPES = 'https://www.googleapis.com/auth/drive https://mail.google.com/'
# SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')
APPLICATION_NAME = 'Accouting Automation'

def get_credentials():
    print("get_credentials()")

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'accounting-automation.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
