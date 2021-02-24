class TestStrategy():
    def __init__(self, scan_results):
        self.scan_results = scan_results
    
    def when_buy(self):
        return self.scan_results['going_up']

    def when_sell(self):
        return self.scan_results['going_up'] is False
