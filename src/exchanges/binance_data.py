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


def get_klines(symbol, interval='1d', limit=14):
    candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)  
    
    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    
    return df

def get_historical_klines(symbol, interval, start_str, end_str=None):
    """
    Fetch historical price data from Binance for a given symbol and interval.
    """
    candles = client.get_historical_klines(symbol, interval, start_str, end_str=end_str)
    df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    
    # Convert 'open_time' and 'close_time' from milliseconds to datetime
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    
    return df


def calculate_rsi(df, period=14):
    """
    Calculate RSI for a given symbol and interval.
    """
    # Make a copy of the dataframe to avoid SettingWithCopyWarning
    df = df.copy()

    # Calculate price changes using .loc for safer operation
    df.loc[:, 'change'] = df['close'].diff()

    # Split gains and losses
    gains = df['change'].where(df['change'] > 0, 0)
    losses = -df['change'].where(df['change'] < 0, 0)
    
    # Calculate average gains and losses
    avg_gain = gains.rolling(window=period, min_periods=period).mean().iloc[-1]
    avg_loss = losses.rolling(window=period, min_periods=period).mean().iloc[-1]
    
    # Calculate RS and RSI
    RS = avg_gain / avg_loss if avg_loss != 0 else 0
    RSI = 100 - (100 / (1 + RS))
    
    return RSI


def calculate_ma(df, period=200):
    """
    Calculate the Simple Moving Average (MA) for a given symbol and period.
    """       
    # Calculate the MA
    ma = df['close'].tail(period).mean()

    return ma


def calculate_macd(df):
    """
    Calculate the MACD and Signal line for a given symbol.
    """
    df_copy = df.copy()
    
    # Calculate the EMAs for MACD
    exp1 = df_copy['close'].ewm(span=12, adjust=False).mean()
    exp2 = df_copy['close'].ewm(span=26, adjust=False).mean()
    df_copy['macd'] = exp1 - exp2
    df_copy['signal_line'] = df_copy['macd'].ewm(span=9, adjust=False).mean()
    
    # Latest MACD and Signal line values
    macd_line = df_copy['macd'].iloc[-1]
    signal_line = df_copy['signal_line'].iloc[-1]

    return macd_line, signal_line


def calculate_bollinger_bands(df, period, std_dev_factor=2):
    """
    Calculate Bollinger Bands for a given symbol.
    """
    df_copy = df.copy()
    
    # Calculate SMA for the given period
    df_copy['middle_band'] = df_copy['close'].rolling(window=period).mean()
    
    # Calculate Standard Deviation
    df_copy['std_dev'] = df_copy['close'].rolling(window=period).std()
    
    # Calculate Upper and Lower Bands
    df_copy['upper_band'] = df_copy['middle_band'] + (df_copy['std_dev'] * std_dev_factor)
    df_copy['lower_band'] = df_copy['middle_band'] - (df_copy['std_dev'] * std_dev_factor)

    return df_copy['upper_band'].iloc[-1], df_copy['middle_band'].iloc[-1], df_copy['lower_band'].iloc[-1]


def calculate_fibonacci_retracement_levels(df):
    high = pd.to_numeric(df['high']).max()
    low = pd.to_numeric(df['low']).min()

    levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    retracements = {'high': high, 'low': low}

    for level in levels:
        # Correctly formatting the key and ensuring arithmetic operations on numbers
        retracements[f'{level:.1%}'.replace('%', '')] = high - (high - low) * level

    return retracements