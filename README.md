# vpn_connect

This repo contains simple scripts to quickly connect to cisco vpn or openvpen.
This will only work if you have your credentials storde in bitwarden.

## Initial setup

```bash
# init virtual environment with
python3 -m venv .venv 

# activate the env
source .venv/bin/activate

# install dependencies
pip3 install -r requirements.txt

# prepare the env
cp .env.dist .env
```

**Install bitwarden cli**:

[bitwarden-cli via brew](https://formulae.brew.sh/formula/bitwarden-cli)

```bash
brew install bitwarden-cli
```

**Get the info for the .env**:

```bash
bw login
bw list items --search "name-of-your-openvpn-password-entry"
bw list items --search "name-of-your-cisco-password-entry"
bw unlock => Copy the session_id here
```

> The `bw list items` command seems to lock the vault again!
> You need to unlock after every search to get the current session_id

## Connecting to a vpn with the script

Spotlight in macOs should be able to find the *_connect.sh.command files.
Just search for the one matching the VPN and press enter.

## Troubleshooting

Sometimes the copy doesn't work anymore. Most of the times the session timed out.
In this case you need to:

```bash
bw logout
bw login
bw unlock => Copy the session_id here
```

If bitwarden seems to take forever you likely didn't unlock your vault

```bash
bw unlock => Copy the session_id to your .env
```
