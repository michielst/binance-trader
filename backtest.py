from env import *
from models import Ticker, Trade
from src.helpers import get_last_x_items, reverse
from src.strategies.Strategy import Strategy
from src.wallet import get_currency_wallet_value, wallet, get_balance


def create_backtest_trade(symbol, ticker):
    order_price = float(ORDER_INPUT)
    price = float(ticker.price)
    quantity = (order_price) / (price) * 0.9995
    print('{}: BUYING {}{} at {}{} => {}{}'.format(ticker.datetime, quantity,
                                                   symbol, price, CURRENCY, (quantity * price), CURRENCY))

    # TODO: Figure out calculations
    sale = order_price / price
    fee = (sale / 100) * 0.1
    # total = sale - fee
    total = price

    Trade.create(currency=symbol, quantity=quantity, price=ticker.price, fee=fee, total=total,
                 type='buy', date=ticker.datetime, epoch=ticker.epoch, test=True)


def create_backtest_sell(symbol, ticker):
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


def start():
    for symbol in SYMBOLS:
        tickers = reverse(Ticker.select().where(Ticker.currency == symbol,
                                                Ticker.epoch > 1614297600).order_by(-Ticker.epoch))

        for i in range(len(tickers)):
            last_30_tickers = reverse(get_last_x_items(tickers, i, 30))

            if len(last_30_tickers) < 30:
                continue

            strategy = Strategy(last_30_tickers, test=True)

            if strategy.when_buy():
                create_backtest_trade(symbol, strategy.ticker)

            if strategy.when_sell():
                create_backtest_sell(symbol, strategy.ticker)

    wallet(test=True)


start()
