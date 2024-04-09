import math
from datetime import datetime

from env import *
from models import Orders
from src.helpers import round_down
from src.data import get_local_quantity

from binance.client import Client
from binance.exceptions import BinanceAPIException
from src.exchanges.binance_data import get_balance

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def buy(symbol, input=ORDER_INPUT):
    symbol = '{}{}'.format(symbol, CURRENCY)
    order_price = float(input)
    trades = client.get_recent_trades(symbol=symbol)
    price = float(trades[0]['price'])
    quantity = order_price / price
    info = client.get_symbol_info(symbol=symbol)
    stepSize = float(info['filters'][2]['stepSize'])
    precision = int(round(-math.log(stepSize, 10), 0))

    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=(round(quantity, precision)))

    print(order)

    quantity = 0
    commission = 0
    for fill in order['fills']:
        commission += float(fill['commission'])
        quantity += float(fill['qty'])

    quantity = quantity - commission
    price = float(order['fills'][0]['price'])
    total = float(order['cummulativeQuoteQty'])
    fee = commission * price

    now = datetime.now()
    Orders.create(symbol=symbol, quantity=quantity, price=price, fee=fee, total=total, type='buy', date=now)

def sell(symbol):
    symbol = '{}{}'.format(symbol, CURRENCY)
    balance = get_balance(symbol)
    quantity = get_local_quantity(symbol)

    if quantity > 0:
        info = client.get_symbol_info(symbol=symbol)
        stepSize = float(info['filters'][2]['stepSize'])
        precision = int(round(-math.log(stepSize, 10), 0))

        if quantity >= balance:
            quantity = balance

        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=round_down(quantity, precision)
        )

        print(order)

        quantity = 0
        fee = 0
        for fill in order['fills']:
            fee += float(fill['commission'])
            quantity += float(fill['qty'])

        price = float(order['fills'][0]['price'])
        total = float(order['cummulativeQuoteQty'])
        total = total - fee

        now = datetime.now()
        Orders.create(symbol=symbol, quantity=quantity, price=price, fee=fee, total=total, type='sell', date=now)
