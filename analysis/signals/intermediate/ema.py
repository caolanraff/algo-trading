'''
The Exponential Moving Average (EMA) represents an average of prices, but places more weight on recent prices.
The weighting applied to the most recent price depends on the selected period of the moving average.
The shorter the period for the EMA, the more weight that will be applied to the most recent price.
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import matplotlib.pyplot as plt
from utils.data import load_financial_data


### Get data
start_date = '2014-01-01'
end_date = '2018-01-01'
ticker = 'GOOG'
SRC_DATA_FILENAME = ticker + '_data.pkl'

data = load_financial_data(ticker, start_date, end_date, SRC_DATA_FILENAME)
data = data.tail(620)
close = data['Close']


### Algo logic
num_periods = 20             # number of days over which to average
K = 2 / (num_periods + 1)    # smoothing constant
ema_p = 0
ema_values = []              # to hold computed EMA values

for close_price in close:
    if ema_p == 0:         # first observation, EMA = current price
        ema_p = close_price
    else:
        ema_p = (close_price - ema_p) * K + ema_p
    ema_values.append(ema_p)

data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(Exponential20DayMovingAverage=pd.Series(ema_values, index=data.index))
print(data.tail(10))


### Charting
close_price = data['ClosePrice']
ema = data['Exponential20DayMovingAverage']

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel=f'{ticker} price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ema.plot(ax=ax1, color='b', lw=2., legend=True)
plt.show()