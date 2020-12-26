from urllib.parse import urlencode, unquote, parse_qs
import json
from pathlib import Path

with open(Path("./secrets.json")) as fh:
    secrets = json.load(fh)

# See docs here for initial setup: https://developer.tdameritrade.com/content/simple-auth-local-apps
# This lib handles all of this (pretty much) automatically: https://github.com/areed1192/td-ameritrade-python-api

# Step 1: Create a TD Ameritrade app

# Step 2: Hit auth endpoint
# print(urlencode({"redirect_uri": "https://127.0.0.1", "client_id": ""}))  # client_key here for encode

# Step 3: Copy and decode auth code returned in `code` parameter
# a = unquote("", encoding='ascii', errors='strict')  # authorization_code here for decode
# print(a)

# Step 4: hit the access token endpoint
