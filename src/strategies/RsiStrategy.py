from env import CURRENCY
from models import Trade
from src.exchanges.binance_data import get_klines, calculate_rsi, calculate_ma, calculate_macd, calculate_bollinger_bands
from pandas import DataFrame

class RsiStrategy():
    def __init__(self, symbol, price, test=False, simulate=False, simulate_df=None):
        self.test = test
        self.symbol = symbol
        self.price = float(price)

        if simulate and isinstance(simulate_df, DataFrame):
            self.df = simulate_df
        else:
            market = self.symbol + CURRENCY
            # Fetching enough data to cover all indicators, considering their look-back periods.
            # The maximum look-back here is for MA200, plus a buffer for MACD calculations.
            self.df = get_klines(market, '1h', 200 + 26)  # Adding 26 periods for MACD's longer EMA.
            self.calculate_indicators()
            self.log()

        # Trades
        self.buys = Trade.select().where(Trade.test == self.test, Trade.currency == self.symbol, Trade.type == 'buy').count()
        self.sells = Trade.select().where(Trade.test == self.test, Trade.currency == self.symbol, Trade.type == 'sell').count()
        
    def simulate_indicators(self, current_df):
        self.rsi = calculate_rsi(current_df, 14)
        self.ma200 = calculate_ma(current_df, 200)
        self.macd_line, self.signal_line = calculate_macd(current_df)
        self.upper_band, self.middle_band, self.lower_band = calculate_bollinger_bands(current_df, 20)
    
    def calculate_indicators(self):
        # RSI calculation with a look-back of 14 periods. No additional data needed beyond the 14 periods.
        self.rsi = calculate_rsi(self.df.tail(14 + 1))  # +1 as diff() reduces the effective size by 1
        
        # MA200 calculation needs at least the last 200 periods.
        self.ma200 = calculate_ma(self.df.tail(200))

        # MACD uses EMAs of 12 and 26 periods, and a signal line which is an EMA of the MACD line over 9 periods.
        # Fetching an additional buffer to ensure accurate EMA calculations at the start of the data slice.
        self.macd_line, self.signal_line = calculate_macd(self.df.tail(26 + 9 + 1))  # Buffer for accurate EMA
        
        # Bollinger Bands with a 20-period SMA and standard deviation. Adding buffer for rolling std calculation.
        self.upper_band, self.middle_band, self.lower_band = calculate_bollinger_bands(self.df.tail(20 + 2), 20)  # +2 as a small buffer

    def when_buy(self):
        return True
        
        # Buy logic: Add condition for price touching or crossing below the lower Bollinger Band
        if (self.rsi < 30 and self.price > self.ma200 and self.macd_line > self.signal_line and self.price <= self.lower_band and (self.buys - self.sells) <= 0):
            return True
        return False

    def when_sell(self):
        # Sell logic: Add condition for price touching or crossing above the upper Bollinger Band
        if ((self.rsi > 70 or self.macd_line < self.signal_line) and self.price >= self.upper_band and (self.buys - self.sells) > 0):
            return True
        return False

    def log(self):
        print("{}: RSI={}, MA200={}, MACD={}, Signal={}, Lower Bollinger={}".format(
            self.symbol, self.rsi, self.ma200, self.macd_line, self.signal_line, self.lower_band))

