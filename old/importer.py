import requests
import time
from models import Ticker
from src.Helpers import reverse, calc_diff


class TickerCalculator():
    def __init__(self, currency, epoch, price, volume24h, prev_price):
        self.currency = currency
        self.epoch = epoch
        self.datetime = datetime(epoch)
        self.price = price
        self.volume24h = volume24h
        self.prev_price = prev_price
        if prev_price:
            (self.price_diff_prev, self.price_diff_prev_pct) = calc_diff(
                prev_price, self.price)
        else:
            self.price_diff_prev = None
            self.price_diff_prev_pct = None

    def save(self):
        Ticker.create(currency=self.currency, epoch=self.epoch, datetime=self.datetime, price=self.price, volume24h=self.volume24h,
                      prev_price=self.prev_price, price_diff_prev=self.price_diff_prev, price_diff_prev_pct=self.price_diff_prev_pct)
        print(self)

    def __str__(self):
        return '{}: {}: price: ${}, quoteVolume24h: {}, price_diff: ${}, price_diff_pct: %{}'.format(
            self.currency, self.datetime, self.price, self.volume24h, self.price_diff_prev, self.price_diff_prev_pct)


def datetime(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))


def import_data(currency):
    range_param = '24h'  # 10mi,1h,12h,24h,1w,1m,3m,1y,ytd,all
    url = 'https://api.ethereumdb.com/v1/timeseries?pair={}-USD&range={}&type=line'.format(
        currency, range_param)

    print('fetching data for {}'.format(currency))
    data = reverse(requests.get(url).json())
    print('fetched data for {}'.format(currency))

    for i in range(len(data)):
        curr = data[i]
        prev_price = None
        if i == 0:
            # get latest record from database to calculate prev_data
            last_ticker = Ticker.select().where(
                Ticker.currency == currency, Ticker.datetime < datetime(data[i]['timestamp'])).order_by(Ticker.datetime.desc())
            if last_ticker.exists():
                prev_price = last_ticker[0].price
        else:
            prev_price = data[i-1]['price']

        ticker = TickerCalculator(
            currency=currency, epoch=curr['timestamp'], price=curr['price'], volume24h=curr['quoteVolume24h'], prev_price=prev_price)

        if Ticker.select().where(Ticker.epoch == ticker.epoch, Ticker.currency == currency).exists() is False:
            ticker.save()


currencies = ['ETH', 'BTC', 'XRP', 'DOGE', 'XLM',
              'ALGO', 'COMP', 'MKR', 'USDT', 'DOT', 'ADA',
              'LINK', 'LTC', 'BCH', 'BNB', 'USDC', 'UNI',
              'WBTC', 'AAVE', 'BSV', 'EOS',  'XMR', 'TRX',
              'XEM', 'XTZ', 'THETA', 'SNX', 'ATOM', 'VET',
              'DAI', 'NEO']

for currency in currencies:
    import_data(currency)
