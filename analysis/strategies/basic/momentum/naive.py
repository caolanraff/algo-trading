'''
Naive momentum strategy based on the number of times a price increases or decreases.
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
def naive_momentum(data, nb_conseq_days):
    signals = pd.DataFrame(index=data.index)
    signals['orders'] = 0
    cons_day = 0
    prior_price = 0
    init = True

    for k in range(len(data['Adj Close'])):
        price = data['Adj Close'][k]
        if init:
            prior_price = price
            init = False
        elif price > prior_price:
            if cons_day < 0:
                cons_day = 0
            cons_day += 1
        elif price < prior_price:
            if cons_day > 0:
                cons_day = 0
            cons_day -= 1
        if cons_day == nb_conseq_days:
            signals['orders'][k] = 1
        elif cons_day == -nb_conseq_days:
            signals['orders'][k] = -1

    return signals


ts = naive_momentum(data, 5)


### Charting
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='%s price in $' % ticker)
data["Adj Close"].plot(ax=ax1, color='g', lw=.5)
ax1.plot(ts.loc[ts.orders == 1.0].index, data["Adj Close"][ts.orders == 1.0], '^', markersize=7, color='k')
ax1.plot(ts.loc[ts.orders == -1.0].index, data["Adj Close"][ts.orders == -1.0], 'v', markersize=7, color='k')
plt.legend(["Price", "Buy", "Sell"])
plt.title("Naive Momentum Trading Strategy")
plt.show()