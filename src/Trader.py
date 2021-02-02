from datetime import datetime

from models import Currency, Listing, db

from src.api.NomicsApi import NomicsApi
from src.strategies.TestStrategy import TestStrategy
from src.strategies.SimpleSafeStrategy import SimpleSafeStrategy


class Trader:
    def __init__(self, wallet):
        self.api = NomicsApi()
        self.wallet = wallet

    def buy(self, currency, amount, price):
        print('BUYING {}{} at ${}'.format(
            amount, currency, price))
        Listing.create(currency=currency, amount=amount,
                       price=price, type='buy', date=datetime.now())

    def sell(self, currency, amount, price):
        balance = self.wallet.get(currency)
        if balance['amount'] != 0 and balance['amount'] >= amount:
            print('SELLING {}{} at ${}'.format(
                amount, currency, price))
            Listing.create(currency=currency, amount=amount,
                           price=price, type='sell', date=datetime.now())

    def start(self):
        print('----TRADER STARTED----')
        currencies = Currency.select().group_by(Currency.currency)
        for currency in currencies:
            scan_results = self.scan(currency.currency)
            print(scan_results)

            test_strategy = TestStrategy(scan_results)
            simple_safe_strategy = SimpleSafeStrategy(scan_results)

            self.decide(currency.currency, test_strategy)
            self.decide(currency.currency, simple_safe_strategy)

    def scan(self, currency):
        prices = Currency.select().where(Currency.currency == currency).order_by(
            -Currency.date).limit(30)
        up_count = 0
        down_count = 0
        print('------------------')
        for i in reversed(range(len(prices))):
            prev = prices[i-1]
            curr = prices[i]

            if prev.price == curr.price:
                continue

            diff = round(prev.price - curr.price, 6)
            diff_pct = round((diff / prev.price) * 100, 6)

            if prev.price > curr.price:
                state = '+++'
                up_count += 1
            else:
                state = '---'
                down_count += 1

            date = datetime.strptime(
                curr.date.replace(':00Z', ''), '%Y-%m-%dT%H:%M')
            print('{} ~ {}: ${} {} {}% \tdiff={}$'.format(
                currency, date, curr.price, state, diff_pct, diff))

        start_price = prices[-1].price
        curr_price = prices[0].price
        price_30m_change = curr_price - start_price
        price_30m_change_pct = (price_30m_change / start_price * 100) / 100

        return dict((
            ('up_count', up_count),
            ('down_count', down_count),
            ('going_up', up_count > down_count),
            ('up_down_diff', up_count - down_count),
            ('price_30m_change', price_30m_change),
            ('price_30m_change_pct', price_30m_change_pct),
            ('price_1h_change', prices[-1].price_1h_change),
            ('price_1h_change_pct', prices[-1].price_1h_change_pct),
            ('price_1d_change', prices[-1].price_1d_change),
            ('price_1d_change_pct', prices[-1].price_1d_change_pct),
        ))

    def decide(self, currency, strategy):
        fee_pct = 0.26
        budget_usd = 50
       
        if strategy.when_buy():
            live_price = self.get_live_price(currency)
            fee = (budget_usd / 100) * fee_pct
            price_with_fee = budget_usd - fee
            amount_to_receive = price_with_fee / live_price
            self.buy(currency, amount_to_receive, budget_usd)

        if strategy.when_sell():
            # sell all from this coin.
            amount = self.wallet.get(currency)['amount']
            live_price = self.get_live_price(currency)
            price = amount * live_price
            fee = (price / 100) * fee_pct
            price_to_receive = (amount * live_price) - fee
            self.sell(currency, amount, price_to_receive)

    def get_live_price(self, currency):
        return float(self.api.live(currency)[0]['price'])
