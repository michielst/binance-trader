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


def calculate_ma(symbol, interval, period):
    """
    Calculate the Simple Moving Average (MA) for a given symbol and period.

    Parameters:
    - symbol (str): The symbol to calculate MA for, e.g., 'BTCUSDT'.
    - interval (str): The candlestick interval (e.g., '1h', '1d').
    - period (int): The period to calculate MA over (e.g., 50, 100, 200).

    Returns:
    - float: The MA value.
    """   
    # Fetch historical candlestick data
    candles = client.get_klines(symbol=symbol, interval=interval, limit=period)
    
    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    
    # Calculate the MA
    ma = df['close'].tail(period).mean()

    return ma


def calculate_macd(symbol, interval):
    """
    Calculate the MACD and Signal line for a given symbol.

    Parameters:
    - symbol (str): The symbol to calculate MACD for, e.g., 'BTCUSDT'.
    - interval (str): The candlestick interval (e.g., '1h', '1d').

    Returns:
    - tuple (float, float): A tuple containing the MACD line value and the Signal line value.
    """   
    # Fetch historical candlestick data (we fetch more to ensure accuracy for the EMAs)
    candles = client.get_klines(symbol=symbol, interval=interval, limit=100)  # 100 is chosen to ensure enough data for calculating EMAs
    
    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    
    # Calculate the EMAs for MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # Latest MACD and Signal line values
    macd_line = df['macd'].iloc[-1]
    signal_line = df['signal_line'].iloc[-1]

    return macd_line, signal_line


def calculate_bollinger_bands(symbol, interval, period=20, std_dev_factor=2):
    """
    Calculate Bollinger Bands for a given symbol.

    Parameters:
    - symbol (str): The symbol to calculate Bollinger Bands for, e.g., 'BTCUSDT'.
    - interval (str): The candlestick interval (e.g., '1h', '1d').
    - period (int): The period for SMA calculation, default is 20.
    - std_dev_factor (int): The standard deviation factor, default is 2.

    Returns:
    - tuple of pandas Series: (upper_band, middle_band, lower_band)
    """    
    # Fetch historical candlestick data
    candles = client.get_klines(symbol=symbol, interval=interval, limit=period*2)  # Fetch more to ensure accuracy
    
    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    
    # Calculate SMA for the given period
    df['middle_band'] = df['close'].rolling(window=period).mean()
    
    # Calculate Standard Deviation
    df['std_dev'] = df['close'].rolling(window=period).std()
    
    # Calculate Upper and Lower Bands
    df['upper_band'] = df['middle_band'] + (df['std_dev'] * std_dev_factor)
    df['lower_band'] = df['middle_band'] - (df['std_dev'] * std_dev_factor)

    return df['upper_band'], df['middle_band'], df['lower_band']