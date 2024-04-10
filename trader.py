import sys
from datetime import datetime
import pandas as pd

from env import CURRENCY
from src.exchanges.binance_data import get_klines, get_historical_klines, calculate_fibonacci_retracement_levels
from src.strategies.IndicatorStrategy import IndicatorStrategy
from models import Orders, Balance
from src.exchanges.binance import place_order


def live_trade(symbol, test=True):
    buy_amount = 10  # The fixed amount for each order
    fee_rate = 0.001
    trades_done = 0

    # Fetch live data
    ticker = get_klines(f"{symbol}{CURRENCY}", '1h', 1)  # Assuming get_klines returns the latest data in a DataFrame
    price = float(ticker['close'].iloc[-1])
    
    # Fetch historical data needed for strategy calculations
    df = get_historical_klines(symbol + CURRENCY, '1h', start_str=(datetime.now() - pd.Timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'))
    
    strategy = IndicatorStrategy(symbol, price, test=test, simulate=True, simulate_df=df)
    fib_levels = calculate_fibonacci_retracement_levels(df) 
    strategy.set_fibonacci_levels(fib_levels)
    
    strategy.simulate_indicators(df)
           
    open_orders = Orders.select().where(Orders.symbol == symbol, Orders.is_open == True, Orders.test == test)
    if not open_orders.exists() and strategy.when_buy():
        fee = buy_amount * fee_rate
        quantity = (buy_amount - fee) / price
        trades_done += 1
        place_order(symbol, quantity, price, fee, 'buy', test)
        
    elif open_orders.exists() and strategy.when_sell():
        # Assuming there's only one open order at a time
        open_order = open_orders.get()
        fee = open_order.quantity * price * fee_rate
        trades_done += 1
        place_order(symbol, open_order.quantity, price, fee, 'sell', test)
        open_order.is_open = False
        open_order.save()
    
    print(f"Live trade completed for {symbol}. Trades done: {trades_done}")

if __name__ == "__main__":
    symbols = sys.argv[1].split(',')  # e.g., "BTC,ETH"

    print("Starting live trading session...")
    for symbol in symbols:
        live_trade(symbol, test=True)
