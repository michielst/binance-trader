from src.helpers import calc_diff
from models import Trade, Ticker


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

        return self.diff_pct <= -3  # <= -5

    def when_sell(self):
        if len(self.tickers) != 30:
            return False

        if (self.buys - self.sells) == 0:
            return False

        # make sure we dont sell with loss
        last_buy = Trade.select().where(Trade.test == self.test, Trade.currency ==
                                        self.ticker.currency, Trade.type == 'buy').order_by(Trade.date.desc()).get()

        if last_buy.price >= self.ticker.price:
            return False

        (profit, profit_pct) = calc_diff(last_buy.price, self.ticker.price)
        if profit_pct < 0.5:
            return False

        return self.diff_pct >= 2
