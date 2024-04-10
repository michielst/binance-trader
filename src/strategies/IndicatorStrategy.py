from env import CURRENCY
from src.exchanges.binance_data import calculate_fibonacci_retracement_levels, get_klines, calculate_rsi, calculate_ma, calculate_macd, calculate_bollinger_bands
from pandas import DataFrame

class IndicatorStrategy():
    def __init__(self, symbol, price, simulate=False, simulate_df=None):
        self.symbol = symbol
        self.position_held = False
        self.price = float(price)
        self.fib_levels = None

        self.rsi_history = []
        self.macd_line_history = []
        self.signal_line_history = []

        if simulate and isinstance(simulate_df, DataFrame):
            self.df = simulate_df
        else:
            market = self.symbol + CURRENCY
            # Fetching enough data to cover all indicators, considering their look-back periods.
            # The maximum look-back here is for MA200, plus a buffer for MACD calculations.
            self.df = get_klines(market, '1h', 200 + 26)  # Adding 26 periods for MACD's longer EMA.
            self.calculate_indicators()
            self.log()
       
       
    def set_fibonacci_levels(self, levels):
        self.fib_levels = levels
         

    def log(self):
        print("{}: RSI={}, MA200={}, MACD={}, Signal={}, Lower Bollinger={}".format(
            self.symbol, self.rsi, self.ma200, self.macd_line, self.signal_line, self.lower_band))
        

    def simulate_indicators(self, current_df):
        self.rsi = calculate_rsi(current_df, 14)
        self.rsi_history.append(self.rsi)

        self.ma200 = calculate_ma(current_df, 200)
        
        self.macd_line, self.signal_line = calculate_macd(current_df)        
        self.macd_line_history.append(self.macd_line)
        self.signal_line_history.append(self.signal_line)
    
        self.upper_band, self.middle_band, self.lower_band = calculate_bollinger_bands(current_df, 20)

        # Limit the history size to the last few entries to avoid unbounded growth
        self.rsi_history = self.rsi_history[-2:]
        self.macd_line_history = self.macd_line_history[-2:]
        self.signal_line_history = self.signal_line_history[-2:]


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
        
        self.fib_levels = calculate_fibonacci_retracement_levels(self.df)


    def when_buy(self):   
        if (self.rsi < 30 or (self.macd_line > self.signal_line and self.price <= self.lower_band)):
            self.position_held = True
            return True
        
        return False

    def when_sell(self):
        if (self.rsi > 70 or self.macd_line < self.signal_line) and self.price >= self.upper_band:
            self.position_held = False
            return True
        
        return False


    # def when_buy(self):
    #     # Criteria for considering a buy:
    #     # 1. Price is near a Fibonacci support level.
    #     # 2. RSI indicates the asset is oversold but improving.
    #     # 3. MACD line has recently crossed above the signal line, indicating bullish momentum.
    #     if len(self.rsi_history) < 2:
    #         return False  # Not enough data
        
    #     rsi_oversold_improving = self.rsi_history[-1] > self.rsi_history[-2] > 30
    #     macd_cross = self.macd_line_history[-1] > self.signal_line_history[-1] and self.macd_line_history[-2] <= self.signal_line_history[-2]

    #     near_fib_support = any(self.price <= level * 1.03 and self.price > level for level in [self.fib_levels['23.6'], self.fib_levels['38.2'], self.fib_levels['61.8']])
    
    #     if near_fib_support and rsi_oversold_improving and macd_cross:
    #         self.position_held = True
    #         return True
    #     return False

    # def when_sell(self):
    #     # Criteria for considering a sell:
    #     # 1. Price is retreating from or near a Fibonacci resistance level.
    #     # 2. RSI indicates the asset might be overbought and is stabilizing or declining.
    #     # 3. MACD line has recently crossed below the signal line, indicating bearish momentum.
    #     if len(self.rsi_history) < 2 or len(self.macd_line_history) < 2:
    #         return False  # Not enough data

    #     rsi_overbought_stabilizing = self.rsi_history[-1] < self.rsi_history[-2] and self.rsi_history[-1] > 70
    #     macd_cross_bearish = self.macd_line_history[-1] < self.signal_line_history[-1] and self.macd_line_history[-2] >= self.signal_line_history[-2]

    #     # Checking if price is near or has retreated from a Fibonacci resistance level
    #     near_fib_resistance = any(self.price >= level * 0.97 and self.price < level for level in [self.fib_levels['61.8'], self.fib_levels['78.6']]) or self.price >= self.fib_levels['high'] * 0.97

    #     if near_fib_resistance and (rsi_overbought_stabilizing or macd_cross_bearish):
    #         self.position_held = False
    #         return True
    #     return False