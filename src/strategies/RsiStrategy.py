from env import *
from models import Ticker, Trade
from src.helpers import calc_diff
from src.exchanges.binance_data import calculate_rsi, calculate_ma, calculate_macd, calculate_bollinger_bands

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
        rsi = calculate_rsi(self.ticker.currency + 'USDT', '1h', 14)
        ma200 = calculate_ma(self.ticker.currency + 'USDT', '1h', 200)  # 200-period MA for trend
        macd_line, signal_line = calculate_macd(self.ticker.currency + 'USDT', '1h')
        upper_band, middle_band, lower_band = calculate_bollinger_bands(self.ticker.currency + 'USDT', '1h')

        print("{}: RSI={}, MA200={}, MACD={}, Signal={}, Lower Bollinger={}".format(
            self.ticker.currency, rsi, ma200, macd_line, signal_line, lower_band.iloc[-1]))

        # Buy logic: Add condition for price touching or crossing below the lower Bollinger Band
        if (rsi < 30 and self.ticker.price > ma200 and macd_line > signal_line and 
            self.ticker.price <= lower_band.iloc[-1] and (self.buys - self.sells) <= 0):
            return True
        return False

    def when_sell(self):
        rsi = calculate_rsi(self.ticker.currency + 'USDT', '1h', 14)
        ma200 = calculate_ma(self.ticker.currency + 'USDT', '1h', 200)
        macd_line, signal_line = calculate_macd(self.ticker.currency + 'USDT', '1h')
        upper_band, middle_band, lower_band = calculate_bollinger_bands(self.ticker.currency + 'USDT', '1h')

        # Sell logic: Add condition for price touching or crossing above the upper Bollinger Band
        if ((rsi > 70 or macd_line < signal_line) and self.ticker.price >= upper_band.iloc[-1] and 
            (self.buys - self.sells) > 0):
            return True
        return False
