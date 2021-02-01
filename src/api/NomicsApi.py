from src.api.Api import Api


class NomicsApi(Api):
    def __init__(self):
        self.key = ''
        self.api = 'https://api.nomics.com/v1/'

    def currencies(self):
        url = self.api + 'currencies/ticker'

        params = (
            ('key', self.key),
            ('ids', 'BTC,ETH,XRP,XLM,ALGO,DOGE,COMP,MKR,USDT,DOT,ADA,LINK,LTC,BCH,BNB'),
            ('interval', '1h, 1d,30d'),
            ('convert', 'USD'),
            ('per-page', 100),
            ('page', 1)
        )

        return super().get(url, params=params)

    def live(self, currency):
        url = self.api + 'currencies/ticker'

        params = (
            ('key', self.key),
            ('ids', currency),
            ('interval', '1h, 1d,30d'),
            ('convert', 'USD'),
            ('per-page', 100),
            ('page', 1)
        )

        return super().get(url, params=params)
