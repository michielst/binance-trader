from peewee import *

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Ticker(BaseModel):
    symbol = CharField(max_length=10)
    epoch = CharField()
    datetime = DateTimeField()
    price = FloatField()


class Trade(BaseModel):
    symbol = CharField(max_length=10)
    quantity = FloatField()  # Amount received in wallet (fees already subtracted)
    price = FloatField()
    fee = FloatField()  # Total fee paid in CURRENCY
    total = FloatField()  # Total CURRENCY spent or received
    type = CharField(max_length=5)  # 'buy' or 'sell'
    date = DateTimeField() 
