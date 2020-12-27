import requests
from urllib.parse import urlencode, unquote, parse_qs
import json

with open("./secrets.json") as fh:
    secrets = json.load(fh)

qs = urlencode(
    {
        'redirect_uri': 'https://127.0.0.1',
        'client_id': secrets['client_key'],
        'response_type': 'code'
    }
)
token_url = 'https://api.tradestation.com/v2/authorize/%s' % qs
print('Navigate to %s' % token_url)
# redirect_url = input('Paste the redirect URL here:')
# unquote(redirect_url)
print(parse_qs(token_url))
# requests.request('GET', 'https://api.tradestation.com/v2/authorize/%s' % qs)