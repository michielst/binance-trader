import sys
import time
from datetime import datetime

from env import *
from models import Ticker
from src.exchanges.binance_data import get_ticker
from src.exchanges.binance import buy, sell
from src.exchanges.test import test_buy, test_sell
from src.helpers import calc_diff, send_public_telegram
from src.strategies.Strategy import Strategy
from src.wallet import wallet


def log(symbol, diff_pct, price):
    if diff_pct >= 5:
        send_public_telegram('🟢 {} UP %{} (${})'.format(
            symbol, round(diff_pct, 2), round(price, 4)))

    if diff_pct <= -5:
        send_public_telegram('🔴 {} DOWN %{} (${})'.format(
            symbol, round(diff_pct, 2), round(price, 4)))


def trade(symbol, test=False):
    tickers = Ticker.select().where(
        Ticker.currency == symbol).order_by(-Ticker.epoch).limit(30)
    strategy = Strategy(tickers, test)

    if strategy.diff == 0.0:
        return

    print("{}:{} {} \t => %{} \t => {}{}".format(strategy.ticker.datetime.hour,
                                                 strategy.ticker.datetime.minute, symbol, round(strategy.diff_pct, 2), strategy.ticker.price, CURRENCY))

    if TELEGRAM_TOKEN and TELEGRAM_PUBLIC_CHAT_ID:
        log(symbol, strategy.diff_pct, strategy.ticker.price)

    if test is True:
        if strategy.when_buy():
            test_buy(symbol, strategy.ticker)

        if strategy.when_sell():
            test_sell(symbol, strategy.ticker)

    elif test is False:
        if strategy.when_buy():
            buy(symbol)

        if strategy.when_sell():
            sell(symbol)

        # print out current profit percentage when available.
        if hasattr(strategy, 'profit_pct'):
            print('PROFIT_PCT: %{} PROFIT: {}'.format(
                round(strategy.profit_pct, 2), strategy.profit))


def scrape(currency):
    symbol = "{}{}".format(currency, CURRENCY)

    try:
        price = get_ticker(symbol)
        now = datetime.now()
        Ticker.create(currency=currency,
                      price=price['lastPrice'], epoch=now.timestamp(), datetime=now)
    except ValueError as e:
        print(e)


def start(test=False, scrape_preparation_minutes=30):
    starttime = time.time()
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


if len(sys.argv) == 1:
    print('STARTING TRADER. !WARNING: MONEY WILL BE SPENT!')
    start()

if len(sys.argv) > 1:
    arg = sys.argv[1]

    if arg == 'test':
        print('STARTING TEST RUN')
        start(test=True)

    if arg == 'wallet':
        if len(sys.argv) == 3 and sys.argv[2] == 'test':
            wallet(test=True)
        else:
            wallet()

    if arg == 'hard':
        print('HARD START')
        start(scrape_preparation_minutes=0)
