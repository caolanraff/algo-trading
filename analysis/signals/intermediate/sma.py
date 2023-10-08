'''
The Simple Moving Average (SMA) is calculated
 by adding the price of an instrument over a number of time periods
 and then dividing the sum by the number of time periods. The SMA
 is basically the average price of the given time period, with equal
 weighting given to the price of each period.

Simple Moving Average
SMA = ( Sum ( Price, n ) ) / n

Where: n = Time Period
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import statistics as stats
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
time_period = 20        # number of days over which to average
history = []            # to track a history of prices
sma_values = []         # to track simple moving average values

for close_price in close:
  history.append(close_price)
  if len(history) > time_period:        # we remove oldest price because we only average over last 'time_period' prices
    del (history[0])
  sma_values.append(stats.mean(history))

data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(Simple20DayMovingAverage=pd.Series(sma_values, index=data.index))
print(data.tail(10))


### Charting
close_price = data['ClosePrice']
sma = data['Simple20DayMovingAverage']

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel=f'{ticker} price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
sma.plot(ax=ax1, color='r', lw=2., legend=True)
plt.show()