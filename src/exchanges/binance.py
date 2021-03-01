import math
from datetime import datetime

from env import *
from models import Trade

from binance.client import Client
from binance.exceptions import BinanceAPIException

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def get_ticker(symbol):
    try:
        price = client.get_ticker(symbol=symbol)
    except BinanceAPIException as e:
        raise ValueError(e)
    else:
        return price


def buy(currency, input=ORDER_INPUT):
    symbol = '{}{}'.format(currency, CURRENCY)
    order_price = float(input)
    trades = client.get_recent_trades(symbol=symbol)
    price = float(trades[0]['price'])
    quantity = (order_price) / (price) * 0.9995
    info = client.get_symbol_info(symbol=symbol)
    stepSize = float(info['filters'][2]['stepSize'])
    precision = int(round(-math.log(stepSize, 10), 0))

    order = client.create_test_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=(round(quantity, precision)))

    print(order)

    price = order['fills'][0]['price']
    total = float(order['cummulativeQuoteQty'])
    # fee = order['fills'][0]['commission']
    fee = total - input

    now = datetime.now()
    trade = Trade.create(currency=currency, quantity=quantity, price=price, fee=fee, total=total,
                         type='buy', date=now, epoch=now.timestamp(), test=False)
    return trade


def sell(currency, quantity):
    symbol = '{}{}'.format(currency, CURRENCY)

    order = client.create_test_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity
    )

    print(order)

    price = order['cummulativeQuoteQty']
    fee = order['fills'][0]['commission']
    total = price - fee

    now = datetime.now()
    trade = Trade.create(currency=currency, quantity=quantity, price=price, fee=fee, total=total,
                         type='sell', date=now, epoch=now.timestamp(), test=False)

    return trade
