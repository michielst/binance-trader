import pandas as pd
from models import Orders


def get_local_quantity(symbol, test):
    buy_orders = Orders.select().where(Orders.symbol == symbol, Orders.type == 'buy', Orders.test == test)
    sell_orders = Orders.select().where(Orders.symbol == symbol, Orders.type == 'sell', Orders.test == test)
    bought_quantity = sum(Orders.quantity for Orders in buy_orders)
    sold_quantity = sum(Orders.quantity for Orders in sell_orders)
    return bought_quantity - sold_quantity


def create_order(symbol, quantity, price, fee, total, Orders_type, date, test=True):
    """
    Inserts a new Orders record into the database.
    """
    if isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()
        
    Orders.create(
        symbol=symbol,
        quantity=quantity,
        price=price,
        fee=fee,
        total=total,
        type=Orders_type,
        date=date,
        test=test
    )