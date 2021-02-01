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
    while True:
        scraper.start()
        trader.start()
        wallet.balance()

        seconds = 60.0
        time.sleep(seconds - ((time.time() - starttime) % seconds))


start()
