'''
The Bollinger Band (BBANDS) plots upper and lower envelope bands around the price of the instrument.
The width of the bands is based on the standard deviation of the closing prices from a moving average of price.
When prices move outside of these bands, that can be interpreted as a breakout/trend signal or an overbought/oversold signal.

Middle Band = n-period moving average
Upper Band = Middle Band + ( y * n-period standard deviation)
Lower Band = Middle Band - ( y * n-period standard deviation)

Where:
  n = number of periods
  y = factor to apply to the standard deviation value, (typical default for y = 2)
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import statistics as stats
import math as math
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
time_period = 20                      # history length for Simple Moving Average for middle band
stdev_factor = 2                      # Standard Deviation Scaling factor for the upper and lower bands
history = []                          # price history for computing simple moving average
sma_values = []                       # moving average of prices for visualization purposes
upper_band = []                       # upper band values
lower_band = []                       # lower band values

for close_price in close:
  history.append(close_price)
  if len(history) > time_period:      # we only want to maintain at most 'time_period' number of price observations
    del (history[0])

  sma = stats.mean(history)
  sma_values.append(sma)              # simple moving average or middle band
  variance = 0                        # variance is the square of standard deviation

  for hist_price in history:
    variance = variance + ((hist_price - sma) ** 2)

  stdev = math.sqrt(variance / len(history))  # use square root to get standard deviation
  upper_band.append(sma + stdev_factor * stdev)
  lower_band.append(sma - stdev_factor * stdev)

data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(MiddleBollingerBand20DaySMA=pd.Series(sma_values, index=data.index))
data = data.assign(UpperBollingerBand20DaySMA2StdevFactor=pd.Series(upper_band, index=data.index))
data = data.assign(LowerBollingerBand20DaySMA2StdevFactor=pd.Series(lower_band, index=data.index))
print(data.tail(10))


### Charting
close_price = data['ClosePrice']
mband = data['MiddleBollingerBand20DaySMA']
uband = data['UpperBollingerBand20DaySMA2StdevFactor']
lband = data['LowerBollingerBand20DaySMA2StdevFactor']

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel=f'{ticker} price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
mband.plot(ax=ax1, color='b', lw=2., legend=True)
uband.plot(ax=ax1, color='y', lw=2., legend=True)
lband.plot(ax=ax1, color='r', lw=2., legend=True)
plt.show()