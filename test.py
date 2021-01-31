from models import Currency

currencies = Currency.select().where(Currency.currency == 'ETH')

for i in range(len(currencies)):
    prev = currencies[i-1]
    curr = currencies[i]

    if prev.price > curr.price:
        state = 'down'
    else:
        state = 'up'

    print('{}: {}'.format(curr.date, state))
