from urllib.parse import urlencode, unquote, parse_qs
import json
from pathlib import Path
import requests
from sys import exit
import websockets
import asyncio

### AUTH

# See docs here for initial setup: https://developer.tdameritrade.com/content/simple-auth-local-apps
# This lib handles all of this (pretty much) automatically: https://github.com/areed1192/td-ameritrade-python-api

# Step 1: Create a TD Ameritrade app

# Step 2: Hit auth endpoint
# print(urlencode({"redirect_uri": "https://127.0.0.1", "client_id": ""}))  # add client_key here for encode

# Step 3: Copy and decode auth code returned in `code` parameter
# a = unquote("", encoding='ascii', errors='strict')  # authorization_code here for decode
# print(a)

# Step 4: hit the access token endpoint

### SETTING UP A STREAM

# Instructions here: https://developer.tdameritrade.com/content/streaming-data
# requests.request('GET', 'https://developer.tdameritrade.com/user-principal/apis/get/userprincipals-0')


def get_new_token(refresh_token: str, client_id: str) -> (str, str):
    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id
    }
    response = requests.post('https://api.tdameritrade.com/v1/oauth2/token', data=params)
    if not response.ok:
        return None, "Request failed with status code %d (%s)" % (response.status_code, response.text.strip())
    return response.json()['access_token'], None


def _get_user_principles(access_token: str) -> (str, str):
    qs_params = {
        "fields": "streamerSubscriptionKeys,streamerConnectionInfo"
    }
    header_params = {
        "authorization": "Bearer %s" % access_token
    }
    response = requests.request('GET', 'https://api.tdameritrade.com/v1/userprincipals', params=qs_params, headers=header_params)
    if not response.ok:
        return None, "Request failed with status code %d (%s)" % (response.status_code, response.text.strip())
    return response.json()['access_token'], None


def open_stream(access_token: str):
    _get_user_principles(access_token)
    # TODO open up a websocket, then blast a login message out through the websocket. That login message contains user principles data



if __name__ == "__main__":
    with open(Path("./secrets.json")) as fh:
        secrets = json.load(fh)
    new_token, err = get_new_token(secrets["refresh_token"], secrets["client_key"])
    if err:
        exit("Error while refreshing token: %s" % err)
    print("New token:\n%s" % new_token)