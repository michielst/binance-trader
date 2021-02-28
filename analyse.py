import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go  # or plotly.express as px

from src.helpers import calc_diff, get_last_x_items
from models import Ticker, Trade


def figure(symbol):
    # https://plotly.com/python/line-charts/
    fig = go.Figure(layout={
        'yaxis': {'title': 'PRICE axis'},
        'yaxis2': {'title': 'DIFF axis', 'overlaying': 'y', 'side': 'right'}
    })
    tickers = Ticker.select().where(
        Ticker.currency == symbol, Ticker.epoch > 1614297600).order_by(-Ticker.epoch)

    timestamps = []
    prices = []
    diffs = []
    # for ticker in tickers:
    for i in range(len(tickers)):
        timestamps.append(tickers[i].datetime)
        prices.append(tickers[i].price)

        last_30_tickers = get_last_x_items(tickers, i, 30)
        if (len(last_30_tickers) == 30):
            (diff, diff_pct) = calc_diff(
                last_30_tickers[0].price, tickers[i].price)
            diffs.append(diff_pct)

    fig.add_trace(go.Scatter(x=timestamps, y=prices, name=symbol,
                             line=dict(color='dodgerblue', width=4)))

    fig.add_bar(x=timestamps, y=diffs, name='diffs', yaxis='y2', offsetgroup=1)

    # fig.add_trace(go.Scatter(x=timestamps, y=diffs, name=symbol,
    #                          line=dict(color='green', width=4)))

    trades = Trade.select().where(Trade.currency == symbol)

    buy_timestamps = []
    buy_prices = []
    sell_timestamps = []
    sell_prices = []
    for trade in trades:
        if trade.type == 'buy':
            buy_timestamps.append(trade.date)
            buy_prices.append(trade.price)
        if trade.type == 'sell':
            sell_timestamps.append(trade.date)
            sell_prices.append(trade.price)

    fig.add_trace(go.Scatter(x=buy_timestamps, y=buy_prices,
                             mode='markers', line=dict(width=10,
                                                       color='Green'), name='BUY'))

    fig.add_trace(go.Scatter(x=sell_timestamps, y=sell_prices,
                             mode='markers', line=dict(width=10,
                                                       color='Red'), name='SELL'))

    # Edit the layout
    fig.update_layout(title='{} Backtest results'.format(symbol),
                      xaxis_title='Timestamp',
                      yaxis_title='Price')

    fig.show()

    app = dash.Dash()
    app.layout = html.Div([
        dcc.Graph(figure=fig)
    ])

    # Turn off reloader if inside Jupyter
    app.run_server(debug=False, use_reloader=False)


figure(sys.argv[1])
