'''
Turtle Strategy.

Go long when the price reaches the highest price for the last x number of days,
or short when the price reaches its lowest point.
Exit the position when the price crosses the moving average of the last x days.
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import numpy as np
from utils.data import load_financial_data
import matplotlib.pyplot as plt


### Get data
ticker = 'GOOG'
data = load_financial_data(ticker, '2001-01-01', '2018-01-01', 'GOOG_data_large.pkl')


### Algo logic
def turtle(data, window_size):
    signals = pd.DataFrame(index=data.index)
    signals['orders'] = 0
    signals['high'] = data['Adj Close'].shift(1).rolling(window=window_size).max()
    signals['low'] = data['Adj Close'].shift(1).rolling(window=window_size).min()
    signals['avg'] = data['Adj Close'].shift(1).rolling(window=window_size).mean()
    signals['long_entry'] = data['Adj Close'] > signals.high
    signals['short_entry'] = data['Adj Close'] < signals.low
    signals['long_exit'] = data['Adj Close'] < signals.avg
    signals['short_exit'] = data['Adj Close'] > signals.avg
    position = 0

    for k in range(len(signals)):
        if signals['long_entry'][k] and position == 0:
            signals.orders.values[k] = 1
            position = 1
        elif signals['short_entry'][k] and position == 0:
            signals.orders.values[k] = -1
            position = -1
        elif signals['short_exit'][k] and position > 0:
            signals.orders.values[k] = -1
            position = 0
        elif signals['long_exit'][k] and position < 0:
            signals.orders.values[k] = 1
            position = 0
        else:
            signals.orders.values[k] = 0
    return signals


ts = turtle(data, 50)


### Charting
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='%s price in $' % ticker)
data["Adj Close"].plot(ax=ax1, color='g', lw=.5)
ts["high"].plot(ax=ax1, color='g', lw=.5)
ts["low"].plot(ax=ax1, color='r', lw=.5)
ts["avg"].plot(ax=ax1, color='b', lw=.5)
ax1.plot(ts.loc[ts.orders == 1.0].index, data["Adj Close"][ts.orders == 1.0], '^', markersize=7, color='k')
ax1.plot(ts.loc[ts.orders == -1.0].index, data["Adj Close"][ts.orders == -1.0], 'v', markersize=7, color='k')
plt.legend(["Price", "Highs", "Lows", "Average", "Buy", "Sell"])
plt.title("Turtle Trading Strategy")
plt.show()