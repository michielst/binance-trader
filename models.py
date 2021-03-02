from peewee import *

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Ticker(BaseModel):
    currency = CharField(max_length=10)
    epoch = CharField()
    datetime = DateTimeField()
    price = FloatField()


class Trade(BaseModel):
    currency = CharField(max_length=10)
    quantity = FloatField()  # amount received in wallet (fees already subtracted)
    price = FloatField()
    fee = FloatField()  # total fee paid in CURRENCY
    total = FloatField()  # total CURRENCY spent buying or receiving when selling
    type = CharField(max_length=5)
    date = DateTimeField()
    epoch = CharField()
    test = BooleanField()
