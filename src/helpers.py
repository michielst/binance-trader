import decimal
import math

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


def send_private_telegram(text):
    _send_telegram(text, TELEGRAM_PRIVATE_CHAT_ID)


def send_public_telegram(text):
    _send_telegram(text, TELEGRAM_PUBLIC_CHAT_ID)


def _send_telegram(text, chat_id):
    API_BASE = 'https://api.telegram.org/bot'
    url = '{}{}/{}?chat_id={}&text={}'.format(
        API_BASE, TELEGRAM_TOKEN, 'sendMessage', chat_id, text)
    requests.get(url)


def reverse(lst):
    return [ele for ele in reversed(lst)]


def round_down(value, decimals):
    with decimal.localcontext() as ctx:
        d = decimal.Decimal(value)
        ctx.rounding = decimal.ROUND_DOWN
        return round(d, decimals)
