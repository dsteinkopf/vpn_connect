#!/usr/bin/env python
#
# connect to an open VPN
#
# DSTK_2025-01-17
#
# Copied from Ludwig

import os
import subprocess
from subprocess import PIPE, Popen

import pyperclip
from dotenv import load_dotenv

COPY_TOKEN_ONLY = True # True if it should not combine the token and the password and copy it to the clipboard

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

BW_SESSION = os.getenv("BW_SESSION")
CISCO_VPN_PASSWORD_ENTRY_ID = os.getenv("CISCO_VPN_PASSWORD_ENTRY_ID")
CISCO_CONNECTION_NAME = os.getenv("CISCO_CONNECTION_NAME")

def load_password():
    print('receiving password and token from bitwarden')
    vpn_password_query = f'bw get password {CISCO_VPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'
    vpn_totp_query = f'bw get totp {CISCO_VPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'

    password = subprocess.getoutput(vpn_password_query)

    totp = subprocess.getoutput(vpn_totp_query)

    # only use last line of totp output
    totp = totp.split('\n')[-1]

    # only use last line of password output
    password = password.split('\n')[-1]

    if COPY_TOKEN_ONLY:
        return totp
    else:
        return password+totp

def copy_password_to_clipboard(password):
    print('copying password to clipboard')
    print(password)
    pyperclip.copy(password)

def start_tunnelblick_connection():
    print(f'starting configured vpn connection {CISCO_CONNECTION_NAME} with tunnelblick')
    connect_script = f'''
        tell application "Tunnelblick"
            disconnect all
            connect "{CISCO_CONNECTION_NAME}"
            get state of first configuration where name = "{CISCO_CONNECTION_NAME}"
            repeat until result = "CONNECTED" or result = "EXITING"
                delay 1
                get state of first configuration where name = "{CISCO_CONNECTION_NAME}"
            end repeat
        end tell'''

    applescript = Popen(['osascript'], stdin=PIPE)
    applescript.communicate(connect_script.encode())

pwOrToken = load_password()
copy_password_to_clipboard(pwOrToken)
start_tunnelblick_connection()
