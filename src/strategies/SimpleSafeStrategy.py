class SimpleSafeStrategy():
    def __init__(self, scan_results):
        self.scan_results = scan_results
    
    def when_buy(self):
        return self.scan_results['going_up'] and self.scan_results['price_30m_change_pct'] >= 0.02

    def when_sell(self):
        return self.scan_results['going_up'] is False
