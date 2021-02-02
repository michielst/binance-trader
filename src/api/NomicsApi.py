from src.api.Api import Api


class NomicsApi(Api):
    def __init__(self):
        self.key = ''
        self.api = 'https://api.nomics.com/v1/'

    def currencies(self):
        print('API CALL')
        url = self.api + 'currencies/ticker'

        params = (
            ('key', self.key),
            ('ids', 'BTC,ETH,XRP,XLM,ALGO,DOGE,COMP,MKR,USDT,DOT,ADA,LINK,LTC,BCH,BNB,USDC,UNI,WBTC,AAVE,BSV,EOS,XMR,TRX,XEM,XTZ,THETA,SNX,ATOM,VET,DAI,NEO,SUSHI,BUSD,CRO,HT,LEO,MIOTA,SOL,CEL,EGLD,DASH,AVAX,GRT,ZEC,FYI,ETC,DCR,KSM,LUNA,ZIL,WAVES,VGX,NEAR,LRC,RUNE'),
            ('interval', '1h, 1d,30d'),
            ('convert', 'USD'),
            ('per-page', 100),
            ('page', 1)
        )

        return super().get(url, params=params)

    def live(self, ids):
        print('API CALL')
        url = self.api + 'currencies/ticker'

        params = (
            ('key', self.key),
            ('ids', ids),
            ('interval', '1h, 1d,30d'),
            ('convert', 'USD'),
            ('per-page', 100),
            ('page', 1)
        )

        return super().get(url, params=params)
