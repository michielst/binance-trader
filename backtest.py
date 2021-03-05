from env import *
from models import Ticker, Trade
from src.exchanges.test import test_buy, test_sell
from src.helpers import get_last_x_items, reverse
from src.strategies.Strategy import Strategy
from src.wallet import wallet, get_base_wallet_value


def start():
    # remove all previous test trades
    test_trades = Trade.select().where(Trade.test == True)
    for test_trade in test_trades:
        test_trade.delete_instance()

    for symbol in SYMBOLS:
        tickers = reverse(Ticker.select().where(Ticker.currency == symbol,
                                                Ticker.epoch > 1614766446).order_by(-Ticker.epoch))

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
