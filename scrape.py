import requests
from models import Currency
import time


class Api:
    def get(self, url, params):
        return requests.get(url, headers=(()), params=params).json()


class NomicsApi(Api):
    def __init__(self):
        self.key = ''
        self.api = 'https://api.nomics.com/v1/'

    def currencies(self):
        url = self.api + 'currencies/ticker'

        params = (
            ('key', self.key),
            ('ids', 'BTC,ETH,XRP,XLM'),
            ('interval', '1d,30d'),
            ('convert', 'USD'),
            ('per-page', 100),
            ('page', 1)
        )

        return super().get(url, params=params)


def scrape():
    api = NomicsApi()

    currencies = api.currencies()
    for currency in currencies:
        message = "{} ({}): ${} on {}".format(
            currency['name'], currency['currency'], currency['price'], currency['price_timestamp'])
        print(message)

        Currency.create(currency=currency['currency'], name=currency['name'],
                        price=currency['price'], date=currency['price_timestamp'])


def start():
    starttime = time.time()
    while True:
        scrape()
        seconds = 60.0
        time.sleep(seconds - ((time.time() - starttime) % seconds))


start()
