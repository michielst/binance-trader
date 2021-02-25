import math
import time
from datetime import datetime

import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException

from env import *
from models import Ticker, Trade
from strategies import Strategy

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def scrape(currencies):
    tickers = []
    for currency in currencies:
        symbol = "{}{}".format(currency, CURRENCY)
        try:
            price = client.get_ticker(symbol=symbol)
            tickers.append({
                'currency': currency,
                'price': price['lastPrice'],
                'epoch': datetime.now().timestamp(),
                'datetime': datetime.now()
            })
        except BinanceAPIException as e:
            print(e)
        else:
            print("{}: {} price: {}{}".format(
                datetime.now(), symbol, price['lastPrice'], CURRENCY))
    Ticker.insert_many(tickers).execute()


def buy():
    balance = client.get_asset_balance(asset=CURRENCY)
    print(balance)

    for s in SYMBOLS:
        symbol = '{}{}'.format(s, CURRENCY)
        order_price = float(12)
        trades = client.get_recent_trades(symbol=symbol)
        price = float(trades[0]['price'])
        quantity = (order_price) / (price) * 0.9995
        print('Buying {}{} at {}{} => {}{}'.format(
            quantity, s, price, CURRENCY, (quantity * price), CURRENCY))
        info = client.get_symbol_info(symbol=symbol)
        stepSize = float(info['filters'][2]['stepSize'])
        precision = int(round(-math.log(stepSize, 10), 0))
        order = client.create_test_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=(round(quantity, precision)))
        print(order)


def send_telegram(action, text):
    API_BASE = 'https://api.telegram.org/bot'
    url = '{}{}/{}?chat_id={}&text={}'.format(
        API_BASE, TELEGRAM_TOKEN, action, TELEGRAM_CHAT_ID, text)
    requests.get(url)


def log(symbol, diff_pct):
    if diff_pct >= 5.0:
        send_telegram(
            'sendMessage', '{} is UP %{} in the last 30 minutes.'.format(symbol, round(diff_pct, 2)))

    if diff_pct <= -5.0:
        send_telegram(
            'sendMessage', '{} is DOWN %{} in the last 30 minutes.'.format(symbol, round(diff_pct, 2)))


def trade():
    for symbol in SYMBOLS:
        tickers = Ticker.select().where(
            Ticker.currency == symbol).order_by(-Ticker.epoch).limit(30)
        (diff, diff_pct) = calc_diff(tickers[-1].price, tickers[0].price)

        if diff == 0.0:
            continue

        print('{} \t => %{} \t{}{}'.format(
            symbol, round(diff_pct, 2), diff, CURRENCY))

        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            log(symbol, diff_pct)

        strategy = Strategy(tickers[0], tickers)
        strategy.when_buy():
            print('BUY')

        strategy.when_sell():
            print('SELL')


def start():
    starttime = time.time()
    scraper_runs_count = 0
    while True:
        scrape(SYMBOLS)
        scraper_runs_count += 1

        if scraper_runs_count > 0:
            trade()
        else:
            print('starting trader in {} minutes'.format(30 - scraper_runs_count))

        time.sleep(60 - ((time.time() - starttime) % 60))

# start()

# BACKTESTING


def get_last_x_items(items, index, amount):
    last_x = []
    min = index - amount
    for x in range(len(items)):
        if x >= min and x < index:
            last_x.append(items[x])
    return last_x


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


def get_wallet(symbol):
    wallet = Trade.select().where(Trade.currency == symbol).order_by(Trade.date.asc())
    quantity = 0

    if symbol == CURRENCY:
        trades = Trade.select().order_by(Trade.date.asc())

        for trade in trades:
            if trade.type == 'buy':
                quantity -= 12
            if trade.type == 'sell':
                quantity += trade.quantity * trade.price
    else:
        for trade in wallet:
            if trade.type == 'buy':
                quantity += trade.quantity
            elif trade.type == 'sell':
                quantity -= trade.quantity

    return quantity


def backtest():
    for symbol in SYMBOLS:
        tickers = Ticker.select().where(
            Ticker.currency == symbol)

        for i in range(len(tickers)):
            last_30_tickers = get_last_x_items(tickers, i, 30)
            strategy = Strategy(tickers[i], last_30_tickers)

            if strategy.when_buy():
                create_backtest_trade(symbol, tickers[i])

            if strategy.when_sell():
                create_backtest_sell(symbol, tickers[i])

    print('wallet summary:')
    for symbol in SYMBOLS:
        quantity = get_wallet(symbol)
        print('{}: {}'.format(symbol, quantity))
    print('{}: {}'.format(CURRENCY, get_wallet(CURRENCY)))


backtest()
