# Trader

## Setup

Create env.py

```
NOMICS_API_KEY=''
BINANCE_API_KEY=''
BINANCE_API_SECRET=''
CURRENCY = 'EUR'
SYMBOLS = ['ETH', 'BTC', 'XRP', 'DOGE', 'XLM',
           'ADA', 'LINK', 'LTC', 'BCH', 'BNB', 'EOS']
TELEGRAM_TOKEN = ''
TELEGRAM_CHAT_ID = ''
```

Create database tables

```
CREATE TABLE "ticker" (
	"id"	INTEGER NOT NULL,
	"currency"	TEXT NOT NULL,
	"price"	REAL NOT NULL,
	"epoch"	TEXT NOT NULL,
	"datetime"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)
```
