import math
import time
from datetime import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException

from env import *
from helpers import calc_diff, send_telegram
from models import Ticker
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


# def buy():
#     balance = client.get_asset_balance(asset=CURRENCY)
#     print(balance)

#     for s in SYMBOLS:
#         symbol = '{}{}'.format(s, CURRENCY)
#         order_price = float(12)
#         trades = client.get_recent_trades(symbol=symbol)
#         price = float(trades[0]['price'])
#         quantity = (order_price) / (price) * 0.9995
#         print('Buying {}{} at {}{} => {}{}'.format(
#             quantity, s, price, CURRENCY, (quantity * price), CURRENCY))
#         info = client.get_symbol_info(symbol=symbol)
#         stepSize = float(info['filters'][2]['stepSize'])
#         precision = int(round(-math.log(stepSize, 10), 0))
#         order = client.create_test_order(
#             symbol=symbol,
#             side=Client.SIDE_BUY,
#             type=Client.ORDER_TYPE_MARKET,
#             quantity=(round(quantity, precision)))
#         print(order)


def log(symbol, diff_pct):
    if diff_pct >= 5.0:
        send_telegram(
            'sendMessage', '🟢 {} UP %{}'.format(symbol, round(diff_pct, 2)))

    if diff_pct <= -5.0:
        send_telegram(
            'sendMessage', '🔴 {} DOWN %{}'.format(symbol, round(diff_pct, 2)))


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

        if strategy.when_buy():
            print('BUY')

        if strategy.when_sell():
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


start()
