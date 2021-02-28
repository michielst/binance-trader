import math
import sys
import time
from datetime import datetime

from env import *
from models import Ticker
from src.exchanges.binance import get_ticker
from src.helpers import calc_diff, send_telegram
from src.strategies.Strategy import Strategy
from src.wallet import wallet


def scrape(currencies):
    tickers = []
    for currency in currencies:
        symbol = "{}{}".format(currency, CURRENCY)
        price = get_ticker(symbol)
        tickers.append({
            'currency': currency,
            'price': price['lastPrice'],
            'epoch': datetime.now().timestamp(),
            'datetime': datetime.now()
        })
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


def start(test=False):
    starttime = time.time()
    scraper_runs_count = 0
    while True:
        scrape(SYMBOLS)
        scraper_runs_count += 1

        if scraper_runs_count > 30:
            trade()
            # wallet(test=test)
        else:
            print('starting trader in {} minutes'.format(30 - scraper_runs_count))

        time.sleep(60 - ((time.time() - starttime) % 60))


if len(sys.argv) > 0 and sys.argv[1] == 'test':
    print('STARTING TEST RUN')
    start(test=True)
else:
    start()
