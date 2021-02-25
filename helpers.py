def calc_diff(prev, curr):
    diff = curr - prev
    diff_pct = (diff / curr) * 100
    return (diff, diff_pct)
