from peewee import *

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Currency(BaseModel):
    currency = CharField(max_length=10)
    name = CharField()
    price = FloatField()
    date = DateTimeField()
    price_1h_change = FloatField()
    price_1h_change_pct = FloatField()
    price_1d_change = FloatField()
    price_1d_change_pct = FloatField()
    price_30d_change = FloatField()
    price_30d_change_pct = FloatField()


class Listing(BaseModel):
    currency = CharField(max_length=10)
    amount = FloatField()
    price = FloatField()
    type = CharField(max_length=5)
    date = DateTimeField()


class Ticker(BaseModel):
    currency = CharField(max_length=10)
    epoch = CharField()
    datetime = DateTimeField()
    price = FloatField()
    # volume24h = FloatField()
    # prev_price = FloatField()
    # price_diff_prev = FloatField()
    # price_diff_prev_pct = FloatField()
