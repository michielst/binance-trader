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

# def buy():
#     balance = client.get_asset_balance(asset=CURRENCY)
#     print(balance)

#     for s in SYMBOLS:
#         symbol = '{}{}'.format(s, CURRENCY)
#         order_price = float(15)
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


def trade(symbol, test=False):
    tickers = Ticker.select().where(
        Ticker.currency == symbol).order_by(-Ticker.epoch).limit(30)
    strategy = Strategy(tickers, test)

    if strategy.diff == 0.0:
        return

    print('{} \t => %{} \t{}{}'.format(
        symbol, round(strategy.diff_pct, 2), strategy.diff, CURRENCY))

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        log(symbol, strategy.diff_pct)

    if strategy.when_buy():
        print('BUY')

    if strategy.when_sell():
        print('SELL')


def scrape(currency):
    symbol = "{}{}".format(currency, CURRENCY)
    price = get_ticker(symbol)
    now = datetime.now()
    Ticker.create(currency=currency,
                  price=price['lastPrice'], epoch=now.timestamp(), datetime=now)
    print("{}:{} {} => {}{}".format(now.hour, now.minute,
                                    currency, price['lastPrice'], CURRENCY))


def start(test=False):
    starttime = time.time()
    scrape_preparation_minutes = 30
    scraper_runs_count = 0
    while True:
        scraper_runs_count += 1

        for symbol in SYMBOLS:
            scrape(symbol)
            if scraper_runs_count > scrape_preparation_minutes:
                trade(symbol, test)

        if scraper_runs_count < scrape_preparation_minutes:
            print('starting trader in {} minutes'.format(
                scrape_preparation_minutes - scraper_runs_count))

        time.sleep(60 - ((time.time() - starttime) % 60))


if len(sys.argv) > 0 and sys.argv[1] == 'test':
    print('STARTING TEST RUN')
    start(test=True)
else:
    start()
