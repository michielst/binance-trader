from peewee import *
from datetime import datetime

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Balance(Model):
    symbol = CharField(unique=True)
    amount = FloatField(default=100)  # Starting balance for each symbol
    
    class Meta:
        database = db

class Orders(Model):
    symbol = CharField()
    quantity = FloatField()
    price = FloatField()
    fee = FloatField()
    type = CharField()
    date = DateTimeField(default=datetime.now)
    test = BooleanField(default=False)
    is_open = BooleanField(default=True)  # True if the order is open/active
    
    class Meta:
        database = db
        
db.connect()
db.create_tables([Orders, Balance], safe=True)