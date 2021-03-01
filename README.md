# Trader

## Setup

Create env.py

```
NOMICS_API_KEY='' # Only needed for old code
TELEGRAM_TOKEN = ''
TELEGRAM_CHAT_ID = ''
BINANCE_API_KEY=''
BINANCE_API_SECRET=''

# CURRENCY = 'EUR'
# SYMBOLS = ['ETH', 'BTC', 'XRP', 'DOGE', 'XLM', 'ADA', 'LINK', 'LTC', 'BCH', 'BNB', 'EOS', 'GRT', 'DOT', 'SXP', 'YFI']
CURRENCY = 'BUSD'
SYMBOLS = ['BTC', 'ETH', 'ADA', 'BNB', 'XRP', 'LTC', 'LINK', 'XLM', 'BCH', 'DOGE', 'XMR', 'ATOM', 'EOS',
           'TRX', 'IOTA', 'ALGO', 'NEO', 'VET', 'XTZ', 'DASH', 'MKR', 'ETC', 'ZIL', 'RVN', 'ZRX', 'WAVES',
           'BAT', 'ONT', 'NANO', 'LRC', 'ZEC', 'MATIC', 'ICX']
MAX_INPUT = 100
ORDER_INPUT = 15
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

CREATE TABLE "trade" (
	"id"	INTEGER NOT NULL UNIQUE,
	"currency"	TEXT NOT NULL,
	"quantity"	REAL NOT NULL,
	"price"	REAL NOT NULL,
	"fee"	REAL NOT NULL,
	"total"	REAL NOT NULL,
	"date"	TEXT NOT NULL,
	"type"	TEXT NOT NULL,
	"epoch"	TEXT NOT NULL,
	"test"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id")
)
```
