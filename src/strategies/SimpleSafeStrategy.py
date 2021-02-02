class SimpleSafeStrategy():
    def __init__(self, scan_results):
        self.scan_results = scan_results
    
    def when_buy(self):
        return self.scan_results['up_down_diff'] >= 5 and self.scan_results['price_30m_change_pct'] >= 0.01

    def when_sell(self):
        return self.scan_results['up_down_diff'] <= -5 and self.scan_results['price_30m_change_pct'] <= -0.01
