import pandas as pd
from models import Trade


def get_quantity(symbol):
    trades = Trade.select().where(Trade.symbol == symbol)

    quantity = 0

    for trade in trades:
        if trade.type == 'buy':
            quantity += trade.quantity

        if trade.type == 'sell':
            quantity -= trade.quantity

    return quantity
