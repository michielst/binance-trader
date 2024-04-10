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


0 * * * * /path/to/your/project/venv/bin/python /path/to/your/project/your_script.py

```
