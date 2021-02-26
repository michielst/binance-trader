from models import Trade
import requests
from env import *


def calc_diff(prev, curr):
    diff = curr - prev
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
    wallet = Trade.select().where(Trade.currency == symbol).order_by(Trade.date.asc())
    quantity = 0

    if symbol == CURRENCY:
        trades = Trade.select().order_by(Trade.date.asc())

        for trade in trades:
            if trade.type == 'buy':
                quantity -= 12
            if trade.type == 'sell':
                quantity += trade.quantity * trade.price
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
