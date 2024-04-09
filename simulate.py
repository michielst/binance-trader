import pandas as pd
from datetime import datetime, timedelta
from src.exchanges.binance_data import get_historical_klines
from src.strategies.RsiStrategy import RsiStrategy
from env import CURRENCY


def simulate_trades(symbol, interval, start_str, end_str=None, test=True):
    df = get_historical_klines(symbol + CURRENCY, interval, start_str, end_str)
    strategy = RsiStrategy(symbol, price=0, test=test, simulate=True, simulate_df=df)

    initial_balance = 10000
    balance = initial_balance
    position = 0
    
    for index, row in df.iterrows():
        # Define the current slice of df up to this point in time
        current_df = df.iloc[:index + 1]  # Include data up to the current row
        strategy.price = row['close']
        
        # Recalculate indicators with the current slice of data
        strategy.simulate_indicators(current_df)
        # strategy.log()
        
        if strategy.when_buy() and balance > 0:
            position = balance / strategy.price
            balance = 0
            print(f"Bought at {strategy.price}")
        elif strategy.when_sell() and position > 0:
            balance = position * strategy.price
            position = 0
            print(f"Sold at {strategy.price}")

    if position > 0:
        balance += position * df.iloc[-1]['close']
    
    profit = balance - initial_balance
    return profit

# Example usage
symbol = 'ETH'
interval = '1h'
start_str = (datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d %H:%M:%S')
end_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
profit = simulate_trades(symbol, interval, start_str, end_str, test=True)
print(f"Simulated profit over the period: ${profit}")
