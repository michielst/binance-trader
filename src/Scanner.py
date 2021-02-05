from datetime import datetime

from models import Listing

from src.strategies.ScanStrategy import ScanStrategy
from src.Trader import Trader
from src.Wallet import Wallet


class ScanResults:
    def __init__(self, item, state, up_streak, down_streak):
        self.item = item
        self.state = state
        self.up_streak = up_streak
        self.down_streak = down_streak

    def __str__(self):
        return '{} up: {} down: {}'.format(self.item.datetime, self.up_streak, self.down_streak)


class Counter:
    def __init__(self, data):
        self.data = data
        self.up_counter = 0
        self.down_counter = 0
        self.up_streak = 0
        self.down_streak = 0

    def up(self):
        self.up_counter += 1
        self.up_streak += 1
        self.down_streak = 0
        self.state = 'up'

    def down(self):
        self.down_counter += 1
        self.down_streak += 1
        self.up_streak = 0
        self.state = 'down'

    def __str__(self):
        return 'UP: {}, DOWN: {}, UP_STREAK: {}, DOWN_STREAK: {}'.format(
            self.up_counter, self.down_counter, self.up_streak, self.down_streak)

    def count(self):
        states = []
        for item in self.data:
            if item.prev_price is not None and item.price < item.prev_price:
                self.down()
            else:
                self.up()
            states.append(ScanResults(item, self.state,
                                      self.up_streak, self.down_streak))
        return states


class Scanner:
    def __init__(self, data, wallet):
        self.data = data
        self.wallet = wallet
        self.trader = Trader(self.wallet)
        self.fee_pct = 0.26
        self.budget_usd = 10

    def get_last_x_items(self, states, i, amount):
        last_x = []
        min = i - amount
        for x in range(len(states)):
            if x >= min and x < i:
                last_x.append(states[x])
        return last_x

    def start(self):
        states = Counter(self.data).count()

        for i in range(len(states)):
            state = states[i]
            last_30 = self.get_last_x_items(states, i, 30)
            self.decide(state, last_30)

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

    def decide(self, state, last_30):
        strategy = ScanStrategy(state, last_30)

        if strategy.when_buy():
            live_price = state.item.price  # self.get_live_price(currency)
            fee = (self.budget_usd / 100) * self.fee_pct
            price_with_fee = self.budget_usd - fee
            amount_to_receive = price_with_fee / live_price
            self.buy(state.item.currency, amount_to_receive, self.budget_usd)

        elif strategy.when_sell():
            amount = float(self.wallet.get(state.item.currency)['amount'])
            if amount != 0.0:
                # sell all from this coin.
                live_price = state.item.price
                price = amount * live_price
                fee = (price / 100) * self.fee_pct
                price_to_receive = (amount * live_price) - fee
                self.sell(state.item.currency, amount, price_to_receive)
