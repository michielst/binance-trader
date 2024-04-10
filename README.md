# Trader

## Setup

Create env.py

```
BINANCE_API_KEY=''
BINANCE_API_SECRET=''
CURRENCY = 'USDT'

```

Usage on server

```
sudo apt install python3.11-venv

python3 -m venv venv

cd /path/to/your/project

source venv/bin/activate


crontab -e


0 * * * * /home/ubuntu/binance-trader/venv/bin/python /home/ubuntu/binance-trader/trader.py
```
