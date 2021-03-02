from env import *

from binance.client import Client
from binance.exceptions import BinanceAPIException

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def get_ticker(symbol):
    try:
        price = client.get_ticker(symbol=symbol)
    except BinanceAPIException as e:
        raise ValueError(e)
    else:
        return price
