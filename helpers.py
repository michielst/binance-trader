from models import Trade
import requests
from env import *


def calc_diff(prev, curr):
    diff = curr - prev

    if curr == 0:
        return (diff, 0)

    diff_pct = (diff / curr) * 100

    return (diff, diff_pct)


def get_last_x_items(items, index, amount):
    last_x = []
    min = index - amount
    for x in range(len(items)):
        if x >= min and x < index:
            last_x.append(items[x])
    return last_x


def get_wallet(symbol):
    wallet = Trade.select().where(Trade.currency == symbol)
    quantity = 0

    if symbol == CURRENCY:
        trades = Trade.select().order_by(Trade.date.desc())

        total_bought = 0
        total_sold = 0
        value_invested = 0
        highest_value_invested = 0

        for trade in trades:
            if trade.type == 'buy':
                total_bought += trade.quantity * trade.price
                value_invested += trade.quantity * trade.price

            if trade.type == 'sell':
                total_sold += trade.quantity * trade.price
                value_invested -= trade.quantity * trade.price

            if highest_value_invested > value_invested:
                highest_value_invested = value_invested

        print('highest value invested: {}{}'.format(
            highest_value_invested, CURRENCY))
        print('total bought: {}{}'.format(total_bought, CURRENCY))
        print('total sold: {}{}'.format(total_sold, CURRENCY))
        return calc_diff(total_bought, total_sold)
    else:
        for trade in wallet:
            if trade.type == 'buy':
                quantity += trade.quantity
            elif trade.type == 'sell':
                quantity -= trade.quantity

    return quantity


def send_telegram(action, text):
    API_BASE = 'https://api.telegram.org/bot'
    url = '{}{}/{}?chat_id={}&text={}'.format(
        API_BASE, TELEGRAM_TOKEN, action, TELEGRAM_CHAT_ID, text)
    requests.get(url)
