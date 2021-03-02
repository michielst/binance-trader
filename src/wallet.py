from env import *
from models import Trade

from src.exchanges.binance_data import get_ticker
from src.helpers import calc_diff


def wallet(test=False):
    print('------------------WALLET-----------------')
    total_wallet_value = 0
    for symbol in SYMBOLS:
        quantity = get_currency_wallet_value(symbol, test=True)
        if quantity > 0:
            price = get_ticker("{}{}".format(symbol, CURRENCY))
            current_price = quantity * float(price['lastPrice'])
            print('{}: {} \t => {}{}'.format(symbol, round(
                quantity, 4), round(current_price, 4), CURRENCY))
            total_wallet_value += current_price
    print('TOTAL VALUE: \t => {}{}'.format(
        round(total_wallet_value, 4), CURRENCY))

    print('\n--------------TRADES PROFIT--------------')
    (total_bought, total_sold, input_value) = get_base_wallet_value(test=True)

    print('\n--------------TOTAL BALANCE--------------')
    balance = input_value + (total_sold - total_bought) + total_wallet_value
    print('BALANCE: \t => {}'.format(balance))
    (profit, profit_pct) = calc_diff(input_value, balance)
    print('PROFIT/LOSS: \t => {}{}'.format(profit, CURRENCY))
    print('PROFIT/LOSS %: \t => %{}'.format(round(profit_pct, 2)))
    print('CASH BALANCE: \t => {}{} (MAX: {})'.format(
        get_balance(test=test), CURRENCY, MAX_INPUT))


def get_currency_wallet_value(symbol, test=False):
    wallet = Trade.select().where(Trade.currency == symbol, Trade.test == test)
    quantity = 0

    for trade in wallet:
        if trade.type == 'buy':
            quantity += trade.quantity
        elif trade.type == 'sell':
            quantity -= trade.quantity

    return quantity


def get_base_wallet_value(test=False):
    trades = Trade.select().where(Trade.test == test).order_by(Trade.date.asc())

    buy_count = 0
    sell_count = 0

    total_bought = 0
    total_sold = 0
    value_invested = 0

    # total amount needed to make these trades (capital needed)
    highest_amount_entered = 0

    for trade in trades:
        order_amount = trade.quantity * trade.price

        if trade.type == 'buy':
            buy_count += 1
            total_bought += order_amount
            value_invested += order_amount

        if trade.type == 'sell':
            sell_count += 1
            total_sold += order_amount
            value_invested -= order_amount

        if value_invested > highest_amount_entered:
            highest_amount_entered = value_invested

    print('BUYS: {} \t => {}{}'.format(buy_count, total_bought, CURRENCY))
    print('SELLS: {} \t => {}{}'.format(sell_count, total_sold, CURRENCY))
    print('INPUT \t\t => {}{}'.format(
        highest_amount_entered, CURRENCY))
    return (total_bought, total_sold, highest_amount_entered)


def get_balance(test=False):
    trades = Trade.select().where(Trade.test == test).order_by(Trade.epoch)

    value = MAX_INPUT

    for trade in trades:
        order_amount = trade.quantity * trade.price

        if trade.type == 'buy':
            value -= order_amount

        if trade.type == 'sell':
            value += order_amount

    return value
