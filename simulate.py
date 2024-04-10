import sys
from datetime import datetime, timedelta
import pandas as pd

from env import CURRENCY
from src.exchanges.binance_data import calculate_fibonacci_retracement_levels, get_historical_klines
from src.strategies.IndicatorStrategy import IndicatorStrategy

def simulate_trades(symbol, initial_balance, interval, start_str, end_str=None, test=True):
    buy_amount = 100
    balance = initial_balance
    crypto_balance = 0
    total_fees_paid = 0
    fee_rate = 0.001
    trades_done = 0
    
    df = get_historical_klines(symbol + CURRENCY, interval, start_str, end_str)
    
    strategy = IndicatorStrategy(symbol, price=0, test=test, simulate=True, simulate_df=df)
    fib_levels = calculate_fibonacci_retracement_levels(df)    
    strategy.set_fibonacci_levels(fib_levels)
    
    for index, row in df.iterrows():
        current_df = df.iloc[:index + 1]
        strategy.price = row['close']
        strategy.simulate_indicators(current_df)
           
        if not strategy.position_held and strategy.when_buy() and balance >= buy_amount:
            fee = buy_amount * fee_rate
            amount_bought = (buy_amount - fee) / strategy.price
            crypto_balance += amount_bought
            balance -= buy_amount
            total_fees_paid += fee
            trades_done += 1
            
        elif strategy.position_held and strategy.when_sell() and crypto_balance > 0:
            gross_value = crypto_balance * strategy.price
            fee = gross_value * fee_rate
            total_fees_paid += fee
            balance += gross_value - fee
            crypto_balance = 0
            trades_done += 1
    
    if crypto_balance > 0:
        gross_value = crypto_balance * df.iloc[-1]['close']
        fee = gross_value * fee_rate
        total_fees_paid += fee
        balance += gross_value - fee
        crypto_balance = 0
    
    profit = balance - initial_balance
    profit_pct = (profit / initial_balance) * 100
    return profit, profit_pct, total_fees_paid, trades_done

symbols = sys.argv[1].split(',')  # e.g., "BTC,ETH"
interval = '1h'
start_str = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')
end_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

initial_balance = 500
total_profit = 0
total_initial_balance = 0
total_fees = 0
total_trades = 0
for symbol in symbols:
    symbol_profit, profit_pct, fees_paid, trades = simulate_trades(symbol, initial_balance, interval, start_str, end_str, test=True)
    total_profit += symbol_profit
    total_initial_balance += initial_balance  
    total_fees += fees_paid
    total_trades += trades
    print(f"{symbol}: Profit: ${symbol_profit:.2f} ({profit_pct:.2f}%), Fees: ${fees_paid:.2f}, Trades: {trades}")

total_profit_pct = (total_profit / total_initial_balance) * 100
print(f"\nTotal profit: ${total_profit:.2f}")
print(f"Total profit percentage: {total_profit_pct:.2f}%")
print(f"Total fees paid: ${total_fees:.2f}")
print(f"Total trades done: {total_trades}")