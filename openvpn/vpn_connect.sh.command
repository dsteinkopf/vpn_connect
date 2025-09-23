#!/bin/bash

# init with
# python3 -m venv venv
# source venv/bin/activate
# pip3 install -r requirements.txt

cd $(dirname $0)
venv/bin/python3 ./vpn_connect.py "$@"
