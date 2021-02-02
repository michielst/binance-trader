class SimpleSafeStrategy():
    def __init__(self, scan_results):
        self.scan_results = scan_results
    
    def when_buy(self):
        if self.scan_results['price_1d_change_pct'] < self.scan_results['price_1h_change_pct']:
            return True

        # return self.scan_results['up_down_diff'] >= 5 and self.scan_results['price_30m_change_pct'] >= 0.01
        return (self.scan_results['up_streak'] >= 5 and self.scan_results['up_down_diff'] >= 5) or self.scan_results['up_down_diff'] >= 10
 
    def when_sell(self):
        # return self.scan_results['up_down_diff'] <= -5 and self.scan_results['price_30m_change_pct'] <= -0.01
        return self.scan_results['down_streak'] >= 5 or self.scan_results['up_down_diff'] <= -5
