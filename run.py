import sys
import time
from datetime import datetime

from env import *
from models import Ticker
from src.exchanges.binance import get_ticker, buy, sell
from src.helpers import calc_diff, send_telegram
from src.strategies.Strategy import Strategy
from src.wallet import wallet


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

    try:
        price = get_ticker(symbol)
        now = datetime.now()
        Ticker.create(currency=currency,
                      price=price['lastPrice'], epoch=now.timestamp(), datetime=now)
        print("{}:{} {} => {}{}".format(now.hour, now.minute,
                                        currency, price['lastPrice'], CURRENCY))
    except ValueError as e:
        print(e)


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


if len(sys.argv) > 1 and sys.argv[1] == 'test':
    print('STARTING TEST RUN')
    start(test=True)
else:
    start()
