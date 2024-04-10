import math
from datetime import datetime

from env import *
from models import Orders, Balance

from binance.client import Client
from binance.exceptions import BinanceAPIException

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
def place_order(symbol, quantity, price, fee, order_type, test=True):
    symbol_with_currency = f"{symbol}{CURRENCY}"
    
    # Calculate the adjusted quantity according to Binance's step size
    info = client.get_symbol_info(symbol_with_currency)
    step_size = float(info['filters'][2]['stepSize'])
    precision = int(round(-math.log(step_size, 10), 0))
    adjusted_quantity = math.floor(quantity / step_size) * step_size

    try:
        if order_type == 'buy':
            order_response = client.create_order(
                symbol=symbol_with_currency,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=round(adjusted_quantity, precision))
        else:  # For sell
            order_response = client.create_order(
                symbol=symbol_with_currency,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=round_down(adjusted_quantity, precision))

        # Calculate total based on the order response
        total = sum(float(fill['price']) * float(fill['qty']) for fill in order_response['fills'])
        
        # Update balance after the execution
        if order_type == 'buy':
            update_balance(symbol, total + fee, adding=False)
        else:
            update_balance(symbol, total - fee, adding=True)

        # Log order details
        print(f"{'BUY' if order_type == 'buy' else 'SELL'} order executed for {symbol}. Quantity: {adjusted_quantity}, Price: {price}, Fee: {fee}, Total: {total}")

        # Save the order to the database
        Orders.create(symbol=symbol, quantity=adjusted_quantity, price=price, fee=fee, total=total, type=order_type, test=test, is_open=order_type == 'buy')
        
    except BinanceAPIException as e:
        print(f"Error executing {'buy' if order_type == 'buy' else 'sell'} order for {symbol}: {e}")


def round_down(value, decimals):
    factor = 10 ** decimals
    return math.floor(value * factor) / factor

# def get_balance(symbol):
#     balance, created = Balance.get_or_create(symbol=symbol)
#     return balance.amount

def update_balance(symbol, amount, adding=False):
    balance, _ = Balance.get_or_create(symbol=symbol)
    if adding:
        balance.amount += amount
    else:
        balance.amount -= amount
    balance.save()