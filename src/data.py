from pandas import pd
from models import Trade

def create_trade_record(symbol, quantity, price, fee, total, trade_type, date):
    if isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()

    Trade.create(
        currency=symbol,
        quantity=quantity,
        price=price,
        fee=fee,
        total=total,
        type=trade_type,
        date=date
    )
    