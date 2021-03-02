from env import *
from models import Trade
from src.wallet import get_currency_wallet_value


def test_buy(symbol, ticker):
    order_price = float(ORDER_INPUT)
    price = float(ticker.price)
    quantity = order_price / price
    print('{}: BUYING {}{} at {}{} => {}{}'.format(ticker.datetime, quantity,
                                                   symbol, price, CURRENCY, (quantity * price), CURRENCY))

    # TODO: Fix correct calculations
    fee_currency = (quantity / 100) * 0.1
    quantity = quantity - fee_currency
    fee = fee_currency * price
    total = order_price + fee

    Trade.create(currency=symbol, quantity=quantity, price=price, fee=fee, total=total,
                 type='buy', date=ticker.datetime, epoch=ticker.epoch, test=True)


def test_sell(symbol, ticker):
    quantity = get_currency_wallet_value(symbol, test=True)

    if quantity > 0:
        print('{}: SELLING {}{} at {}{} => {}{}'.format(ticker.datetime, quantity, symbol,
                                                        ticker.price, CURRENCY, (quantity * ticker.price), CURRENCY))

        price = ticker.price
        sale = price * quantity
        fee = (sale / 100) * 0.1
        total = sale - fee

        Trade.create(currency=symbol, quantity=quantity, price=ticker.price, fee=fee, total=total,
                     type='sell', date=ticker.datetime, epoch=ticker.epoch, test=True)
