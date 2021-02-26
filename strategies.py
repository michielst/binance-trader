from helpers import calc_diff
from models import Trade


class Strategy():
    def __init__(self, ticker, last_30_tickers):
        self.ticker = ticker
        self.last_30_tickers = last_30_tickers

        self.buys = Trade.select().where(
            Trade.currency == self.ticker.currency, Trade.type == 'buy').count()
        self.sells = Trade.select().where(Trade.currency == self.ticker.currency,
                                          Trade.type == 'sell').count()

        if len(self.last_30_tickers) == 30:
            (self.diff, self.diff_pct) = calc_diff(
                self.last_30_tickers[0].price, self.ticker.price)

    def when_buy(self):
        if len(self.last_30_tickers) != 30:
            return False

        if (self.buys - self.sells) > 0:
            return False

        return self.diff_pct <= -3  # <= -5

    def when_sell(self):
        if len(self.last_30_tickers) != 30:
            return False

        if (self.buys - self.sells) == 0:
            return False

        # make sure we dont sell with loss
        last_buy = Trade.select().where(
            Trade.currency == self.ticker.currency, Trade.type == 'buy').order_by(Trade.date.desc()).get()
        if last_buy.price >= self.ticker.price:
            return False

        return self.diff_pct >= 2
