import sys
from datetime import datetime, timedelta
import pandas as pd

from env import CURRENCY
from src.exchanges.binance_data import calculate_fibonacci_retracement_levels, get_historical_klines
from src.strategies.IndicatorStrategy import IndicatorStrategy

def simulate_trades(symbol, interval, start_str, end_str=None, test=True):
    buy_amount = 10000
    initial_balance = 10000
    balance = initial_balance
    crypto_balance = 0  # Track the amount of cryptocurrency bought
    total_fees_paid = 0  # Track total fees paid
    fee_rate = 0.001  # Binance fee rate of 0.10%
    
    df = get_historical_klines(symbol + CURRENCY, interval, start_str, end_str)
    
    strategy = IndicatorStrategy(symbol, price=0, test=test, simulate=True, simulate_df=df)
    
    fib_levels = calculate_fibonacci_retracement_levels(df)    
    strategy.set_fibonacci_levels(fib_levels)
    
    for index, row in df.iterrows():
        current_df = df.iloc[:index + 1]
        strategy.price = row['close']
        strategy.simulate_indicators(current_df)
                
        if not strategy.position_held and strategy.when_buy() and balance >= buy_amount:
            # Calculate fees and adjust buy_amount if necessary
            fee = buy_amount * fee_rate
            amount_bought = (buy_amount - fee) / strategy.price
            crypto_balance += amount_bought  # Update crypto balance
            balance -= buy_amount  # Deduct the buy_amount (including fee) from the balance
            total_fees_paid += fee
            # print(f"Bought {amount_bought} {symbol} at {strategy.price}, fee: {fee:.2f} USD, Value: {buy_amount - fee:.2f} USD ({row['open_time']})")
            
        elif strategy.position_held and strategy.when_sell() and crypto_balance > 0:
            gross_value = crypto_balance * strategy.price
            fee = gross_value * fee_rate
            total_fees_paid += fee
            balance += gross_value - fee
            # print(f"Sold {crypto_balance} {symbol} at {strategy.price}, fee: {fee:.2f} USD, Value: {gross_value - fee:.2f} USD ({row['open_time']})")
            crypto_balance = 0
    
    if crypto_balance > 0:
        gross_value = crypto_balance * df.iloc[-1]['close']
        fee = gross_value * fee_rate
        total_fees_paid += fee
        balance += gross_value - fee
        crypto_balance = 0
    
    profit = balance - initial_balance
    print(f"Final fiat balance: ${balance:.2f}, Total fees paid: ${total_fees_paid:.2f}")
    profit_pct = (profit / initial_balance) * 100
    print(f"Simulated profit with {symbol} over the period: ${profit:.2f} ({profit_pct:.2f}%)")
    return profit

symbols = sys.argv[1].split(',') # BTC, ETH
interval = '1h'
start_str = (datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d %H:%M:%S')
end_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

for symbol in symbols:
    profit = simulate_trades(symbol, interval, start_str, end_str, test=True)
   

