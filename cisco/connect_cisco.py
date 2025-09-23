#!/usr/bin/env python3
#
# Connect to a cisco vpn
#
# DSTK_2025-09-16 copied from vpn_connect.py
#
# /opt/cisco/secureclient/bin/vpn connect "Name of the VPN Profile"
# /opt/cisco/secureclient/bin/vpn disconnect


import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

VPN_PATH = "/opt/cisco/secureclient/bin/vpn"

VPN_PROFILE = os.getenv("VPN_PROFILE")
BW_SESSION = os.getenv("BW_SESSION")
VPN_PASSWORD_ENTRY_ID = os.getenv("VPN_PASSWORD_ENTRY_ID")

def load_credentials():
    print('receiving password and token from bitwarden')
    vpn_username_query = f'bw get username {VPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'
    vpn_password_query = f'bw get password {VPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'
    vpn_totp_query = f'bw get totp {VPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'

    username = subprocess.getoutput(vpn_username_query).split('\n')[-1]
    password = subprocess.getoutput(vpn_password_query).split('\n')[-1]
    token = subprocess.getoutput(vpn_totp_query).split('\n')[-1]
    return username, password, token

def start_cisco_vpn(username, password, token):
    process = subprocess.Popen(
        [VPN_PATH, "-s"],
        stdin=subprocess.PIPE,
        text=True
    )
    commands = f"""connect "{VPN_PROFILE}"
{username}
{password}
{token}
"""
    process.communicate(commands)

if __name__ == "__main__":
    username, password, token = load_credentials()
    start_cisco_vpn(username, password, token)
