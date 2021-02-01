from models import Currency

from src.api.NomicsApi import NomicsApi


class Scraper:
    def __init__(self):
        self.api = NomicsApi()

    def start(self):
        print('----SCRAPER STARTED----')
        api = NomicsApi()
        currencies = api.currencies()

        for currency in currencies:
            # message = "{} ({}): ${} on {}".format(
            #     currency['name'], currency['currency'], currency['price'], currency['price_timestamp'])
            # print(message)

            Currency.create(currency=currency['currency'], name=currency['name'],
                            price=currency['price'], date=currency['price_timestamp'],
                            price_1h_change=currency['1h']['price_change'],
                            price_1h_change_pct=currency['1h']['price_change_pct'],
                            price_1d_change=currency['1d']['price_change'],
                            price_1d_change_pct=currency['1d']['price_change_pct'],
                            price_30d_change=currency['30d']['price_change'],
                            price_30d_change_pct=currency['30d']['price_change_pct'])
