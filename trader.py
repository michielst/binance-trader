import sys
import time
from datetime import datetime

from env import *
from models import Tickers
from src.exchanges.binance_data import get_ticker
from src.exchanges.binance import buy, sell
from src.strategies.IndicatorStrategy import IndicatorStrategy


def trade(symbol, test=False):
    ticker = get_ticker("{}{}".format(symbol, CURRENCY))
    strategy = IndicatorStrategy(symbol, ticker['price'], test)

    if test is True:
        if strategy.when_buy():
            print(f"Buy")

        if strategy.when_sell():
            print(f"Sell")

    elif test is False:
        if strategy.when_buy():
            buy(symbol)

        if strategy.when_sell():
            sell(symbol)

def collect(symbol):
    market = "{}{}".format(symbol, CURRENCY)

    try:
        price = get_ticker(market)
        if price is not None:
            now = datetime.now()
            Tickers.create(symbol=symbol, price=price['price'], date=now)
    except ValueError as e:
        print(e)


def start(test=False, scrape_preparation_minutes=0):
    starttime = time.time()
    scraper_runs_count = 0

    while True:
        scraper_runs_count += 1

        for symbol in SYMBOLS:
            collect(symbol)
            
            if scraper_runs_count > scrape_preparation_minutes:
                trade(symbol, test)

        if scraper_runs_count < scrape_preparation_minutes:
            print(f"starting trader in {scrape_preparation_minutes - scraper_runs_count} minutes")

        time.sleep(60 - ((time.time() - starttime) % 60))


if len(sys.argv) == 1:
    print('STARTING TRADER. !WARNING: MONEY WILL BE SPENT!')
    start()

if len(sys.argv) > 1:
    arg = sys.argv[1]

    if arg == 'test':
        print('STARTING TEST RUN')
        start(test=True)

    if arg == 'hard':
        print('HARD START')
        start(scrape_preparation_minutes=0)
