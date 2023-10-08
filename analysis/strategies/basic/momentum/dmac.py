'''
Dual moving average crossover
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
def double_moving_average(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['orders'] = signals['signal'].diff()
    return signals


ts = double_moving_average(data, 20, 100)


### Charting
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='%s price in $' % ticker)
data["Adj Close"].plot(ax=ax1, color='g', lw=.5)
ts["short_mavg"].plot(ax=ax1, color='r', lw=2.)
ts["long_mavg"].plot(ax=ax1, color='b', lw=2.)
ax1.plot(ts.loc[ts.orders == 1.0].index, data["Adj Close"][ts.orders == 1.0], '^', markersize=7, color='k')
ax1.plot(ts.loc[ts.orders == -1.0].index, data["Adj Close"][ts.orders == -1.0], 'v', markersize=7, color='k')
plt.legend(["Price", "Short mavg", "Long mavg", "Buy", "Sell"])
plt.title("Double Moving Average Trading Strategy")
plt.show()