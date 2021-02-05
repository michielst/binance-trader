from src.Helpers import calc_diff


class ScanStrategy():
    def __init__(self, state, last_30):
        self.state = state
        self.last_30 = last_30

        if len(self.last_30) == 30:
            (self.diff, self.diff_pct) = calc_diff(
                self.last_30[0].item.price, self.state.item.price)

    def when_buy(self):
        if len(self.last_30) != 30:
            return False

        return self.diff_pct > 2

    def when_sell(self):
        if len(self.last_30) != 30:
            return False

        return self.diff_pct < -6
