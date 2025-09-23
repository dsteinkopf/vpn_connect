#!/usr/bin/env python
#
# connect Redcare VPN
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

load_dotenv()

BW_SESSION = os.getenv("BW_SESSION")
VPN_PASSWORD_ENTRY_ID = os.getenv("VPN_PASSWORD_ENTRY_ID")
CONNECTION_NAME = os.getenv("CONNECTION_NAME")
# mac_connection_path = '/Library/Application Support/Tunnelblick/Users/stk/dSteinkopf@de-cgn01-fw01.my-eav.net.tblk'

def load_password():
    print('receiving password and token from bitwarden')
    vpn_password_query = f'bw get password {VPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'
    vpn_totp_query = f'bw get totp {VPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'

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
    print(f'starting configured vpn connection {CONNECTION_NAME} with tunnelblick')
    connect_script = f'''
        tell application "Tunnelblick"
            disconnect all
            connect "{CONNECTION_NAME}"
            get state of first configuration where name = "{CONNECTION_NAME}"
            repeat until result = "CONNECTED" or result = "EXITING"
                delay 1
                get state of first configuration where name = "{CONNECTION_NAME}"
            end repeat
        end tell'''

    applescript = Popen(['osascript'], stdin=PIPE)
    applescript.communicate(connect_script.encode())

pwOrToken = load_password()
copy_password_to_clipboard(pwOrToken)
start_tunnelblick_connection()
