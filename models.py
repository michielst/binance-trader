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
    quantity = FloatField()
    price = FloatField()
    type = CharField(max_length=5)
    date = DateTimeField()
    epoch = CharField()
    test = BooleanField()
