from models import Listing
from src.api.NomicsApi import NomicsApi


class Wallet:
    def __init__(self):
        self.api = NomicsApi()

    def balance(self):
        print('----WALLET----')
        listing_currencies = Listing.select().group_by(Listing.currency)

        profit_loss = 0
        total_wallet_value = 0
        total_spent = 0

        for currency in listing_currencies:
            balance = self.get(currency.currency)
            live_value = float(self.api.live(currency.currency)[0]['price'])
            current_value = balance['amount'] * live_value
            diff = current_value - balance['value']

            print('{}{} \t= ${} \tProfit/Loss: ${} \tSpent ${}'.format(
                round(balance['amount'], 2),
                currency.currency,
                round(current_value, 6),
                round(diff, 6),
                round(balance['value'], 6)))

            profit_loss += diff
            total_wallet_value += current_value
            total_spent += balance['value']

        print('--Balance--')
        print('Total wallet value: ${} \tSpent ${}'.format(
            total_wallet_value, total_spent))
        print('Total profit/loss: ${}'.format(profit_loss))

    def get(self, currency):
        listings = Listing.select().where(
            Listing.currency == currency).order_by(Listing.date.asc())

        value = 0
        amount = 0
        for listing in listings:
            if listing.type == 'buy':
                amount += listing.amount
                value += listing.price
            elif listing.type == 'sell':
                amount -= listing.amount
                value -= listing.price

        return dict((('value', value), ('amount', amount)))
