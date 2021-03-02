from env import *
from models import Ticker
from src.exchanges.test import test_buy, test_sell
from src.helpers import get_last_x_items, reverse
from src.strategies.Strategy import Strategy
from src.wallet import wallet


def start():
    for symbol in SYMBOLS:
        tickers = reverse(Ticker.select().where(Ticker.currency == symbol,
                                                Ticker.epoch > 1614592800).order_by(-Ticker.epoch))

        for i in range(len(tickers)):
            last_30_tickers = reverse(get_last_x_items(tickers, i, 30))

            if len(last_30_tickers) < 30:
                continue

            strategy = Strategy(last_30_tickers, test=True)

            if strategy.when_buy():
                test_buy(symbol, strategy.ticker)

            if strategy.when_sell():
                test_sell(symbol, strategy.ticker)

    wallet(test=True)


start()
