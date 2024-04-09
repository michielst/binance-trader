from env import *

from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def get_ticker(symbol):
    try:
        price = client.get_symbol_ticker(symbol=symbol)
    except BinanceAPIException as e:
        raise ValueError(e)
    else:
        return price


def get_balance(symbol):
    try:
        balance = client.get_asset_balance(asset=symbol)
    except BinanceAPIException as e:
        raise ValueError(e)
    else:
        return float(balance['free'])

def calculate_rsi(symbol, interval='1d', period=14):
    """
    Calculate RSI for a given symbol and interval.
    
    Parameters:
    - symbol (str): The symbol to calculate RSI for, e.g., 'BTCUSDT'.
    - interval (str): The candlestick interval (e.g., '1h', '1d').
    - period (int): The period to calculate RSI over (typically 14).
    
    Returns:
    - float: The RSI value.
    """
    
    # Fetch historical candlestick data
    candles = client.get_klines(symbol=symbol, interval=interval, limit=period*2)  # Fetch enough data to ensure accurate RSI calculation
    
    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    
    # Calculate price changes
    df['change'] = df['close'].diff()
    
    # Split gains and losses
    gains = df['change'].where(df['change'] > 0, 0)
    losses = -df['change'].where(df['change'] < 0, 0)
    
    # Calculate average gains and losses
    avg_gain = gains.rolling(window=period, min_periods=period).mean().iloc[-1]
    avg_loss = losses.rolling(window=period, min_periods=period).mean().iloc[-1]
    
    # Calculate RS and RSI
    RS = avg_gain / avg_loss if avg_loss != 0 else 0  # Prevent division by zero
    RSI = 100 - (100 / (1 + RS))
    
    return RSI