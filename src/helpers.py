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


def send_telegram(action, text):
    API_BASE = 'https://api.telegram.org/bot'
    url = '{}{}/{}?chat_id={}&text={}'.format(
        API_BASE, TELEGRAM_TOKEN, action, TELEGRAM_CHAT_ID, text)
    requests.get(url)
