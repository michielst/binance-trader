import requests


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
            ('ids', 'BTC,ETH,XRP'),
            ('interval', '1d,30d'),
            ('convert', 'USD'),
            ('per-page', 100),
            ('page', 1)
        )

        return super().get(url, params=params)


api = NomicsApi()

currencies = api.currencies()

for currency in currencies:
    message = "{} ({}): ${} on {}".format(
        currency['name'], currency['currency'], currency['price'], currency['price_date'])
    print(message)
