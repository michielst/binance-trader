import sys
import time

from env import *
from src.exchanges.binance_data import get_ticker
from src.exchanges.binance import buy, sell
from src.exchanges.test import test_buy, test_sell
from src.strategies.RsiStrategy import RsiStrategy
from src.wallet import wallet


def trade(symbol, test=False):
    ticker = get_ticker("{}{}".format(symbol, CURRENCY))
    strategy = RsiStrategy(symbol, ticker['price'], test)

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

        # # print out current profit percentage when available.
        # if hasattr(strategy, 'profit_pct'):
        #     print('PROFIT_PCT: %{} PROFIT: {}'.format(
        #         round(strategy.profit_pct, 2), strategy.profit))


# def scrape(currency):
#     symbol = "{}{}".format(currency, CURRENCY)

#     try:
#         price = get_ticker(symbol)
#         if price is not None:
#             now = datetime.now()
#             Ticker.create(currency=currency,
#                           price=price['price'], epoch=now.timestamp(), datetime=now)
#     except ValueError as e:
#         print(e)


def start(test=False, scrape_preparation_minutes=0):
    starttime = time.time()
    scraper_runs_count = 0

    while True:
        scraper_runs_count += 1

        for symbol in SYMBOLS:
            # scrape(symbol)
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
