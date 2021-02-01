from datetime import datetime

from models import Currency, Listing, db

from src.api.NomicsApi import NomicsApi


class Trader:
    def __init__(self, wallet):
        self.api = NomicsApi()
        self.wallet = wallet

    def start(self):
        print('----TRADER STARTED----')
        currencies = Currency.select().group_by(Currency.currency)
        for currency in currencies:
            results = self.scan(currency.currency)
            self.decide(currency.currency, results)

    def scan(self, currency):
        prices = Currency.select().where(Currency.currency == currency).limit(60)
        up_count = 0
        down_count = 0
        for i in range(len(prices)):
            prev = prices[i-1]
            curr = prices[i]

            if prev.price == curr.price:
                continue

            diff = round(prev.price - curr.price, 2)
            diff_pct = round((diff / prev.price) * 100, 2)

            if prev.price > curr.price:
                state = '+++'
                up_count += 1
            else:
                state = '---'
                down_count += 1

            date = datetime.strptime(
                curr.date.replace(':00Z', ''), '%Y-%m-%dT%H:%M')
            # print('{}: {} {}% \tdiff={}$'.format(date, state, diff_pct, diff))
        return dict((
            ('up_count', up_count),
            ('down_count', down_count),
            ('price_1d_change', prices[-1].price_1d_change),
            ('price_1d_change_pct', prices[-1].price_1d_change_pct),
        ))

    def decide(self, currency, scan_results):
        going_up = scan_results['up_count'] >= scan_results['down_count']
        amount = 1

        live_price = float(self.api.live(currency)[0]['price'])

        if going_up and scan_results['price_1d_change_pct'] >= 0.02:
            self.buy(currency, amount, amount * live_price)

        if going_up is False and scan_results['price_1d_change_pct'] <= 0:
            amount = self.wallet.get(currency)['amount']
            self.sell(currency, amount, amount * live_price)

    def buy(self, currency, amount, price):
        print('BUYING {}{} at ${}'.format(amount, currency, price))
        Listing.create(currency=currency, amount=amount,
                       price=price, type='buy', date=datetime.now())

    def sell(self, currency, amount, price):
        balance = self.wallet.get(currency)
        if (balance['amount'] > amount):
            print('SELLING {}{} at ${}'.format(amount, currency, price))
            Listing.create(currency=currency, amount=amount,
                           price=price, type='sell', date=datetime.now())
