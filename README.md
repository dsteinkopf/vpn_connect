# Setup

**init virtual environment with**:

```bash
python3 -m venv .venv
```

**activate the env**:

```bash
source .venv/bin/activate
```

**install dependencies**:

```bash
pip3 install -r requirements.txt
```

**prepare the env**:

```bash
cp .env.dist .env
```

## Install bitwarden cli

[bitwarden-cli via brew](https://formulae.brew.sh/formula/bitwarden-cli)

```bash
brew install bitwarden-cli
```

## Get the info for the .env

```bash
bw login
bw unlock => Copy the session_id here
bw list items --search "name-of-your-openvpn-password-entry"
bw list items --search "name-of-your-cisco-password-entry"
```

The response contains the entry id which you will need for the .env variables.

## Troubleshooting

Sometimes the copy doesn't work anymore. Most of the times the session timed out.
In this case you need to:

```bash
bw logout
bw login
bw unlock => Copy the session_id here
```

## Connecting to a vpn with the script

Spotlight in macOs should be able to find the *_connect.sh.command files.
Just search for the one matching the VPN and press enter.
