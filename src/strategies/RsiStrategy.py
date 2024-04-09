from env import *
from models import Ticker, Trade
from src.helpers import calc_diff
from src.exchanges.binance_data import calculate_rsi 

class RsiStrategy():
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
        # Calculate RSI based on the symbol from the most recent data
        # Assuming symbol is like 'BTCUSDT' and is stored in self.ticker.currency in a compatible format
        rsi = calculate_rsi(self.ticker.currency + 'USDT', '1h', 14)  # Example for hourly data

        print("{}: {}RSI".format(self.ticker.currency, rsi)) 

        # Implement buy logic based on RSI
        if rsi < 30 and (self.buys - self.sells) <= 0:
            # RSI indicates oversold, potential buy opportunity
            return True
        return False

    def when_sell(self):
        # Calculate RSI for selling decision
        rsi = calculate_rsi(self.ticker.currency + 'USDT', '1h', 14)  # Same assumption as above

        # Implement sell logic based on RSI
        if rsi > 70 and (self.buys - self.sells) > 0:
            # RSI indicates overbought, potential sell opportunity
            return True
        return False