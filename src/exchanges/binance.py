import math
from datetime import datetime

from env import *
from models import Trade
from src.helpers import send_private_telegram
from src.wallet import get_currency_wallet_value

from binance.client import Client
from binance.exceptions import BinanceAPIException

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def buy(currency, input=ORDER_INPUT):
    symbol = '{}{}'.format(currency, CURRENCY)
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

    quantity = float(order['fills'][0]['qty'])
    commission = float(order['fills'][0]['commission'])
    quantity = quantity - commission
    price = float(order['fills'][0]['price'])
    total = float(order['cummulativeQuoteQty'])
    fee = commission * price

    now = datetime.now()
    Trade.create(currency=currency, quantity=quantity, price=price, fee=fee, total=total,
                 type='buy', date=now, epoch=now.timestamp(), test=False)

    if TELEGRAM_TOKEN and TELEGRAM_PRIVATE_CHAT_ID:
        send_private_telegram(
            '{} {} BOUGHT FOR {}{}'.format(quantity, currency, CURRENCY, total))


def sell(currency):
    symbol = '{}{}'.format(currency, CURRENCY)
    quantity = get_currency_wallet_value(currency)

    if quantity > 0:
        info = client.get_symbol_info(symbol=symbol)
        stepSize = float(info['filters'][2]['stepSize'])
        precision = int(round(-math.log(stepSize, 10), 0))

        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=round(quantity, precision)
        )

        print(order)

        quantity = float(order['fills'][0]['qty'])
        price = float(order['fills'][0]['price'])
        fee = float(order['fills'][0]['commission'])
        total = float(order['cummulativeQuoteQty'])
        total = total - fee

        now = datetime.now()
        Trade.create(currency=currency, quantity=quantity, price=price, fee=fee, total=total,
                     type='sell', date=now, epoch=now.timestamp(), test=False)

        if TELEGRAM_TOKEN and TELEGRAM_PRIVATE_CHAT_ID:
            send_private_telegram('{} {} SOLD FOR {}{}'.format(
                quantity, currency, CURRENCY, total))
