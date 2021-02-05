from models import Ticker
from src.Scanner import Scanner
from src.Wallet import Wallet

wallet = Wallet()
currencies = Ticker.select().group_by(Ticker.currency)

for currency in currencies:
    tickers = Ticker.select().where(
        Ticker.currency == currency.currency, Ticker.epoch > 1612469565)
    scanner = Scanner(tickers, wallet)
    scanner.start()

wallet.balance()
