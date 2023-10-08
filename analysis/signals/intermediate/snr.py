'''
Support and Resistance
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.data import load_financial_data


### Get data
start_date = '2014-01-01'
end_date = '2018-01-01'
ticker = 'GOOG'
SRC_DATA_FILENAME = ticker + '_data.pkl'

data = load_financial_data(ticker, start_date, end_date, SRC_DATA_FILENAME)
data = data.tail(620)
lows = data['Low']
highs = data['High']


### Analaysis
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel = f'{ticker} price in $')
lows.plot(ax=ax1, color='y', lw=2.)
highs.plot(ax=ax1, color='c', lw=2.)
plt.hlines(lows.head(200).min(), lows.index.values[0], lows.index.values[-1], linewidth=2, color='g')       # support line
plt.hlines(highs.head(200).max(), lows.index.values[0], lows.index.values[-1], linewidth=2, color='r')      # resistance line
plt.axvline(linewidth=2, color='b', x=lows.index.values[200], linestyle=':')
plt.show()


### Algo logic
signal = pd.DataFrame(index=data.index)
signal['price'] = data['Adj Close']

def trading_support_resistance(data, bin_width=20):
    data['sup_tolerance'] = pd.Series(np.zeros(len(data)))
    data['res_tolerance'] = pd.Series(np.zeros(len(data)))
    data['sup_count'] = pd.Series(np.zeros(len(data)))
    data['res_count'] = pd.Series(np.zeros(len(data)))
    data['sup'] = pd.Series(np.zeros(len(data)))
    data['res'] = pd.Series(np.zeros(len(data)))
    data['positions'] = pd.Series(np.zeros(len(data)))
    data['signal'] = pd.Series(np.zeros(len(data)))
    in_support = 0
    in_resistance = 0

    for x in range((bin_width - 1) + bin_width, len(data)):
        data_section = data[x - bin_width:x + 1]
        support_level = min(data_section['price'])
        resistance_level = max(data_section['price'])
        range_level = resistance_level - support_level
        data['res'][x] = resistance_level
        data['sup'][x] = support_level
        data['sup_tolerance'][x] = support_level + 0.2 * range_level
        data['res_tolerance'][x] = resistance_level - 0.2 * range_level

        if data['price'][x] >= data['res_tolerance'][x] and data['price'][x] <= data['res'][x]:
            in_resistance += 1
            data['res_count'][x] = in_resistance
        elif data['price'][x] <= data['sup_tolerance'][x] and data['price'][x] >= data['sup'][x]:
            in_support += 1
            data['sup_count'][x] = in_support
        else:
            in_support = 0
            in_resistance = 0

        if in_resistance > 2:
            data['signal'][x] = 1
        elif in_support > 2:
            data['signal'][x] = 0
        else:
            data['signal'][x] = data['signal'][x-1]

    data['positions'] = data['signal'].diff()

trading_support_resistance(signal)
print(signal.tail(20))


### Charting
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel = f'{ticker} price in $')
signal['sup'].plot(ax=ax1, color='g', lw=2.)
signal['res'].plot(ax=ax1, color='b', lw=2.)
signal['price'].plot(ax=ax1, color='r', lw=2.)
ax1.plot(signal.loc[signal.positions == 1.0].index, signal.price[signal.positions == 1.0], '^', markersize = 7, color = 'k', label = 'buy')
ax1.plot(signal.loc[signal.positions == -1.0].index, signal.price[signal.positions == -1.0], 'v', markersize = 7, color = 'k', label = 'sell')
plt.legend()
plt.show()