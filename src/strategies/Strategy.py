from env import *
from models import Ticker, Trade
from src.helpers import calc_diff
from src.wallet import get_balance


class Strategy():
    def __init__(self, tickers, test=False):
        self.test = test
        self.tickers = tickers
        self.ticker = self.tickers[0]
        self.start_ticker = self.tickers[-1]

        (self.diff, self.diff_pct) = calc_diff(
            self.start_ticker.price, self.ticker.price)

        self.buys = Trade.select().where(Trade.test == self.test, Trade.currency ==
                                         self.ticker.currency, Trade.type == 'buy').count()
        self.sells = Trade.select().where(Trade.test == self.test, Trade.currency ==
                                          self.ticker.currency, Trade.type == 'sell').count()

    def when_buy(self):
        if len(self.tickers) != 30:
            return False

        if (self.buys - self.sells) > 0:
            return False

        if get_balance(test=self.test) < ORDER_INPUT:
            return False

        if self.diff_pct >= -4:
            return False

        last_hour_tickers = Ticker.select().where(Ticker.currency == self.ticker.currency).order_by(-Ticker.epoch).limit(60)
        (last_hour_diff, last_hour_diff_pct) = calc_diff(last_hour_tickers[0].price, self.ticker.price)

        return last_hour_diff_pct <= 6

    def when_sell(self):
        if len(self.tickers) != 30:
            return False

        if (self.buys - self.sells) == 0:
            return False

        # make sure we dont sell with loss
        last_buy = Trade.select().where(Trade.test == self.test, Trade.currency ==
                                        self.ticker.currency, Trade.type == 'buy').order_by(Trade.date.desc()).get()

        (profit, profit_pct) = calc_diff(last_buy.price, self.ticker.price)
        self.profit_pct = profit_pct
        self.profit = (last_buy.quantity * self.ticker.price) - \
            (last_buy.quantity * last_buy.price)

        # sell at loss when -10%
        # if profit_pct <= -10:
        #     return True

        if last_buy.price >= self.ticker.price or profit_pct <= 5:
            return False

        if profit_pct >= 5:
            return True

        return self.diff_pct >= 2.75
