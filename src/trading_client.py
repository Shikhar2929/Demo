from __future__ import annotations

import json
import urllib.request

from src.orderbook import OrderBook
from src.websocket_client import WebSocketClient


class TradingClient:
    def __init__(
        self, http_endpoint: str, ws_endpoint: str, username: str, api_key: str
    ):
        self._http_endpoint = http_endpoint
        self._ws_endpoint = ws_endpoint
        self._username = username
        self._api_key = api_key

        self._user_buildup()

    def _user_buildup(self):
        """Authenticate the user and obtain a session token."""
        form_data = {"username": self._username, "apiKey": self._api_key}
        req = urllib.request.Request(
            self._http_endpoint + "/buildup",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        self._session_token = response.get("sessionToken")
        self._orderbook = OrderBook(json.loads(response["orderBookData"]))
        self._client = WebSocketClient(
            endpoint=self._ws_endpoint, orderbook=self._orderbook
        )

        return response

    def place_limit(self, ticker: str, volume: float, price: float, is_bid: bool):
        """Place a Limit Order on the exchange."""
        if not self._session_token:
            raise Exception("User not authenticated. Call user_buildup first.")

        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
            "ticker": ticker,
            "volume": volume,
            "price": price,
            "isBid": is_bid,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/limit_order",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        return json.loads(urllib.request.urlopen(req).read().decode("utf-8"))

    def place_market(self, ticker: str, volume: float, is_bid: bool):
        """Place a Market Order on the exchange."""
        if not self._session_token:
            raise Exception("User not authenticated. Call user_buildup first.")

        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
            "ticker": ticker,
            "volume": volume,
            "isBid": is_bid,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/market_order",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        content = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        print(content)

    def remove_all(
        self,
    ):
        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/remove_all",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(req).read().decode("utf-8")
        print("Remove all response:", response)
        return json.loads(response)

    def get_details(self):
        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/get_details",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(req).read().decode("utf-8")
        print("Get details response:", response)
        return json.loads(response)

    async def subscribe(self):
        await self._client.subscribe()

    async def unsubscribe(self):
        await self._client.unsubscribe()
