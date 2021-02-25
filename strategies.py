from helpers import calc_diff


class Strategy():
    def __init__(self, ticker, last_30_tickers):
        self.ticker = ticker
        self.last_30_tickers = last_30_tickers

        if len(self.last_30_tickers) == 30:
            (self.diff, self.diff_pct) = calc_diff(
                self.last_30_tickers[0].price, self.ticker.price)

    def when_buy(self):
        if len(self.last_30_tickers) != 30:
            return False

        return self.diff_pct <= -5

    def when_sell(self):
        if len(self.last_30_tickers) != 30:
            return False

        return self.diff_pct >= 2
