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

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

VPN_PATH = "/opt/cisco/secureclient/bin/vpn"

BW_SESSION = os.getenv("BW_SESSION")
OPENVPN_PASSWORD_ENTRY_ID = os.getenv("OPENVPN_PASSWORD_ENTRY_ID")
OPENVPN_PROFILE = os.getenv("OPENVPN_PROFILE")

def load_credentials():
    print('receiving password and token from bitwarden')
    vpn_username_query = f'bw get username {OPENVPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'
    vpn_password_query = f'bw get password {OPENVPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'
    vpn_totp_query = f'bw get totp {OPENVPN_PASSWORD_ENTRY_ID} --session {BW_SESSION}'

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
    commands = f"""connect "{OPENVPN_PROFILE}"
{username}
{password}
{token}
"""
    process.communicate(commands)

if __name__ == "__main__":
    username, password, token = load_credentials()
    start_cisco_vpn(username, password, token)
