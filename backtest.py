from env import *
from models import Trade, Ticker
from helpers import get_last_x_items, get_wallet
from strategies import Strategy


def create_backtest_trade(symbol, ticker):
    order_price = float(12)
    price = float(ticker.price)
    quantity = (order_price) / (price) * 0.9995
    print('{}: BUYING {}{} at {}{} => {}{}'.format(ticker.datetime, quantity,
                                                   symbol, price, CURRENCY, (quantity * price), CURRENCY))
    Trade.create(currency=symbol, quantity=quantity, price=ticker.price,
                 type='buy', date=ticker.datetime, epoch=ticker.epoch)


def create_backtest_sell(symbol, ticker):
    quantity = get_wallet(symbol)

    # sell all for now
    if quantity > 0:
        print('{}: SELLING {}{} at {}{} => {}{}'.format(ticker.datetime, quantity, symbol,
                                                        ticker.price, CURRENCY, (quantity * ticker.price), CURRENCY))
        Trade.create(currency=symbol, quantity=quantity, price=ticker.price,
                     type='sell', date=ticker.datetime, epoch=ticker.epoch)


def start():
    for symbol in SYMBOLS:
        tickers = Ticker.select().where(
            Ticker.currency == symbol, Ticker.epoch > 1614297600)

        for i in range(len(tickers)):
            last_30_tickers = get_last_x_items(tickers, i, 30)
            strategy = Strategy(tickers[i], last_30_tickers)

            if strategy.when_buy():
                create_backtest_trade(symbol, tickers[i])

            if strategy.when_sell():
                # TODO: Only sell when profit? Check with current wallet and buy prices
                create_backtest_sell(symbol, tickers[i])

    print('wallet summary:')
    for symbol in SYMBOLS:
        quantity = get_wallet(symbol)
        print('{}: {}'.format(symbol, quantity))
    print('Profit: {}'.format(get_wallet(CURRENCY)))


start()
