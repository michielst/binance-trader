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
