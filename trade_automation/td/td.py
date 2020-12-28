from urllib.parse import urlencode, unquote, parse_qs
import json
from pathlib import Path
import requests
from sys import exit
import websockets
import asyncio
import datetime
from typing import Dict

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


class TDClient:
    def __init__(self, refresh_token: str, client_id: str):
        self._refresh_token = refresh_token
        self._client_id = client_id
        self._access_token, cerr = self._get_new_token()
        if cerr:
            raise ConnectionError(cerr)

    def _get_new_token(self) -> (str, str):
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self._client_id
        }
        response = requests.post('https://api.tdameritrade.com/v1/oauth2/token', data=params)
        if not response.ok:
            return None, "Request failed with status code %d (%s)" % (response.status_code, response.text.strip())
        return response.json()['access_token'], None

    def _get_user_principles(self) -> (str, str):
        qs_params = {
            "fields": "streamerSubscriptionKeys,streamerConnectionInfo"
        }
        header_params = {
            "authorization": "Bearer %s" % self._access_token
        }
        response = requests.request('GET', 'https://api.tdameritrade.com/v1/userprincipals', params=qs_params, headers=header_params)
        if not response.ok:
            return None, "Request failed with status code %d (%s)" % (response.status_code, response.text.strip())
        return response.json()['access_token'], None

    def open_stream(self):
        self._get_user_principles()
        # TODO open up a websocket, then blast a login message out through the websocket. That login message contains user principles data

    def get_price_history(
            self,
            symbol: str,
            start_date: datetime.datetime,
            period_type: str = "day",
            period: int = 1,
            frequency_type: str = "minute",
            frequency: int = 1,
            need_ext_hours_data: bool = False
        ) -> (Dict, str):
        """
        See https://developer.tdameritrade.com/price-history/apis/get/marketdata/%7Bsymbol%7D/pricehistory
        Note: "frequency" is actually the time between samples
        :return: JSON with candlestick data
        """
        # NOTE the end date parameter is ignored here. Can add it later if needed.
        qs_params = {
            "period_type": period_type,
            "period": period,
            "frequencyType": frequency_type,
            "frequency": frequency,
            "startDate": datetime.datetime.timestamp(start_date),  # TODO left off here
            "needExtendedHoursData": need_ext_hours_data
        }
        header_params = {
            "authorization": "Bearer %s" % self._access_token
        }
        response = requests.request('GET', 'https://api.tdameritrade.com/v1/marketdata/%s/pricehistory' % symbol, params=qs_params, headers=header_params)
        if not response.ok:
            return None, "Request failed with status code %d (%s)" % (response.status_code, response.text.strip())
        return response.json(), None


def sample_hi_lo_auto(
        client: TDClient,
        symbol: str,
        window_start_date: datetime.date=datetime.date.today(),
        window_start_time: datetime.time=datetime.time(8, 30, 00),
        window_duration: datetime.timedelta=datetime.timedelta(0, 30),
    ):
    # capture the high and the low over some period
    price_hist, err = client.get_price_history(
        symbol,
        frequency_type="minute",
        frequency=1,
        start_date=window_start_date,
        period_type="day",
        period=1
    )
    need_ext_hours_data: bool = False
    if err:
        raise ConnectionError(err)
    high = None
    low = None
    for candlestick in price_hist["candles"]:
        if high is None or candlestick["high"] > high:
            high = candlestick["high"]
        if low is None or candlestick["low"] < low:
            low = candlestick["low"]

    for candle in price_hist["candles"]:
        print("%s : %s - %s" % (datetime.datetime.fromtimestamp(float(candle["datetime"]) / 1000), candle["low"], candle["high"]))
    pass
    # TODO define trade logic


if __name__ == "__main__":
    with open(Path("./secrets.json")) as fh:
        secrets = json.load(fh)
    client = TDClient(secrets["refresh_token"], secrets["client_key"])
    sample_hi_lo_auto(
        client,
        "VOO",
        window_start_time=datetime.time(9, 30, 0),
        window_duration=datetime.timedelta(minutes=1),
        window_start_date=datetime.date(2020, 12, 12)
    )
    pass