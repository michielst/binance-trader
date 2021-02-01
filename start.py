import time

from models import Currency
from src.api.NomicsApi import NomicsApi
from src.Scraper import Scraper
from src.Wallet import Wallet
from src.Trader import Trader


def start():
    wallet = Wallet()
    scraper = Scraper()
    trader = Trader(wallet)
    starttime = time.time()

    scraper_runs_count = 0
    while True:
        scraper.start()
        scraper_runs_count += 1

        if scraper_runs_count > 0:
            trader.start()
            wallet.balance()
        else:
            print('starting trader in {} minutes'.format(30 - scraper_runs_count))

        seconds = 60.0
        time.sleep(seconds - ((time.time() - starttime) % seconds))


start()
