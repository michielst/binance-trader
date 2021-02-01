from datetime import datetime

from models import Currency, Listing, db

from src.api.NomicsApi import NomicsApi


class Trader:
    def __init__(self, wallet):
        self.api = NomicsApi()
        self.wallet = wallet

    def buy(self, currency, amount, price):
        fee_pct = 0.26
        fee = (fee_pct / 100) * price
        price_with_fee = price + fee
        print('BUYING {}{} at ${} with ${} fee'.format(
            amount, currency, price, fee))
        Listing.create(currency=currency, amount=amount,
                       price=price_with_fee, type='buy', date=datetime.now())

    def sell(self, currency, amount, price):
        fee_pct = 0.26
        fee = (fee_pct / 100) * price
        price_with_fee = price - fee

        balance = self.wallet.get(currency)
        if (balance['amount'] > amount):
            print('SELLING {}{} at ${} with ${} fee'.format(
                amount, currency, price, fee))
            Listing.create(currency=currency, amount=amount,
                           price=price_with_fee, type='sell', date=datetime.now())

    def start(self):
        print('----TRADER STARTED----')
        currencies = Currency.select().group_by(Currency.currency)
        for currency in currencies:
            results = self.scan(currency.currency)
            self.decide(currency.currency, results)

    def scan(self, currency):
        prices = Currency.select().where(Currency.currency == currency).order_by(
            -Currency.date).limit(30)
        up_count = 0
        down_count = 0
        for i in reversed(range(len(prices))):
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
            print('{}: {} {}% \tdiff={}$'.format(date, state, diff_pct, diff))
        return dict((
            ('up_count', up_count),
            ('down_count', down_count),
            ('price_1h_change', prices[-1].price_1h_change),
            ('price_1h_change_pct', prices[-1].price_1h_change_pct),
            ('price_1d_change', prices[-1].price_1d_change),
            ('price_1d_change_pct', prices[-1].price_1d_change_pct),
        ))

    def decide(self, currency, scan_results):
        going_up = scan_results['up_count'] >= scan_results['down_count']
        diff = scan_results['up_count'] - scan_results['down_count']

        BUYING_WITH_IN_USD = 10.0

        if diff >= 3 and scan_results['price_1d_change_pct'] > 0.1:
            live_price = self.get_live_price(currency)
            amount = BUYING_WITH_IN_USD / live_price
            self.log(currency, going_up, diff, scan_results)
            self.buy(currency, amount, amount * live_price)

        if diff <= -3 and scan_results['price_1h_change_pct'] < 0.1:
            live_price = self.get_live_price(currency)
            amount = self.wallet.get(currency)['amount']

            if amount:
                self.log(currency, going_up, diff, scan_results)
                self.sell(currency, amount, amount * live_price)

    def get_live_price(self, currency):
        return float(self.api.live(currency)[0]['price'])

    def log(self, currency, going_up, diff, scan_results):
        print('currency', currency)
        print('going_up', going_up)
        print('diff', diff)
        print('up_count', scan_results['up_count'])
        print('down_count', scan_results['down_count'])
        print('price_1d_change_pct', scan_results['price_1d_change_pct'])
