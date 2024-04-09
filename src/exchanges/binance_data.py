from env import *

from binance.client import Client
from binance.exceptions import BinanceAPIException

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def get_ticker(symbol):
    try:
        price = client.get_symbol_ticker(symbol=symbol)
    except BinanceAPIException as e:
        raise ValueError(e)
    else:
        return price


def get_balance(symbol):
    try:
        balance = client.get_asset_balance(asset=symbol)
    except BinanceAPIException as e:
        raise ValueError(e)
    else:
        return float(balance['free'])
