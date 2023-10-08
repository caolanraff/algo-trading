'''
Standard Deviation is a statistical calculation used to measure the variability.
In trading this value is known as volatility.
A low standard deviation indicates that the data points tend to be very close to the mean,
whereas high standard deviation indicates that the data points are spread out over a large range of values.
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import statistics as stats
import math
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
time_period = 20        # look back period
history = []            # history of prices
sma_values = []         # to track moving average values for visualization purposes
stddev_values = []      # history of computed stdev values

for close_price in close:
  history.append(close_price)
  if len(history) > time_period:    # we track at most 'time_period' number of prices
    del (history[0])

  sma = stats.mean(history)
  sma_values.append(sma)
  variance = 0                      # variance is square of standard deviation

  for hist_price in history:
    variance = variance + ((hist_price - sma) ** 2)

  stdev = math.sqrt(variance / len(history))
  stddev_values.append(stdev)

data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(StandardDeviationOver20Days=pd.Series(stddev_values, index=data.index))
print(data.tail(10))


### Charting
close_price = data['ClosePrice']
stddev = data['StandardDeviationOver20Days']

fig = plt.figure()
ax1 = fig.add_subplot(211, ylabel=f'{ticker} price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ax2 = fig.add_subplot(212, ylabel='Stddev in $')
stddev.plot(ax=ax2, color='b', lw=2., legend=True)
ax2.axhline(y=stats.mean(stddev_values), color='k')
plt.show()