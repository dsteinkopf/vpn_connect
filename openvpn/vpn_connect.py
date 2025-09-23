#!/usr/bin/env python
#
# connect to an open VPN
#
# DSTK_2025-01-17
#
# Copied from Ludwig

import os
import sys
import argparse
import subprocess
from subprocess import PIPE, Popen

from requests.exceptions import RequestException

import pyperclip
from dotenv import load_dotenv

# Ensure project root (containing the 'lib' package) is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from lib.bitwarden_client import BitwardenClient, BitwardenError

COPY_TOKEN_ONLY = True  # True if it should not combine the token and the password and copy it to the clipboard

load_dotenv()

BW_SESSION = os.getenv("BW_SESSION")
VPN_PASSWORD_ENTRY_ID = os.getenv("VPN_PASSWORD_ENTRY_ID")
CONNECTION_NAME = os.getenv("CONNECTION_NAME")
BW_SERVE_URL = os.getenv("BW_SERVE_URL", "http://127.0.0.1:8087")


def load_password():
    print('receiving password and token from bitwarden via API')
    client = BitwardenClient(serve_url=BW_SERVE_URL, session=BW_SESSION, keep_running=True)
    password = client.get_password(VPN_PASSWORD_ENTRY_ID)
    totp = client.get_totp(VPN_PASSWORD_ENTRY_ID)
    if COPY_TOKEN_ONLY:
        return totp
    else:
        return password + totp


def probe_api() -> int:
    """Check if Vault Management API is usable and if the configured item can be read.
    Returns 0 on success, non-zero on failure.
    """
    print("Probing Bitwarden Vault Management API…")
    try:
        client = BitwardenClient(serve_url=BW_SERVE_URL, session=BW_SESSION, keep_running=True)
        # This will ensure the API is running and can access the item
        client.probe(VPN_PASSWORD_ENTRY_ID)
        print(f"API status: ok at {BW_SERVE_URL}")
        if not BW_SESSION:
            print("Notice: No BW_SESSION provided to the script. If the vault appears locked to the API, set BW_SESSION in .env or export it in your shell after 'bw unlock'.")
        # Try to fetch fields for the configured item without printing secrets
        password = client.get_password(VPN_PASSWORD_ENTRY_ID)
        token = client.get_totp(VPN_PASSWORD_ENTRY_ID)
        print(f"Item access: OK (password {len(password) if password else 'empty'} & TOTP {token} retrievable)")
        return 0
    except (RequestException, BitwardenError, RuntimeError, OSError, FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"Probe failed: {e}")
        print("Hint: Ensure Bitwarden CLI is installed, you're logged in (bw login), and the vault is unlocked (bw unlock).")
        return 1


def copy_password_to_clipboard(password):
    print('copying password to clipboard')
    # Avoid printing the actual secret to stdout for security reasons
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


def main():
    parser = argparse.ArgumentParser(description="Connect VPN after fetching password/TOTP from Bitwarden API.")
    parser.add_argument("--probe", action="store_true", help="Test Bitwarden API connectivity and item access, then exit.")
    args = parser.parse_args()

    if args.probe:
        code = probe_api()
        sys.exit(code)

    try:
        pwOrToken = load_password()
    except (RequestException, BitwardenError, RuntimeError, OSError, FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"Failed to retrieve credentials via API: {e}")
        print("Please ensure 'bw serve' is available and your vault is unlocked (bw unlock).")
        sys.exit(1)

    copy_password_to_clipboard(pwOrToken)
    start_tunnelblick_connection()


if __name__ == "__main__":
    main()
