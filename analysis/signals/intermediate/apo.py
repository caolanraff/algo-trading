'''
The Absolute Price Oscillator (APO) is based on the absolute differences between two moving averages of different lengths.
A ‘Fast’ and a ‘Slow’ moving average.
A large difference is usually interpreted as one of two things:
  - instrument prices are starting to trend or break out
  - instrument prices are far away from their equilibrium prices (overbought / oversold)

APO = Fast Exponential Moving Average - Slow Exponential Moving Average
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
num_periods_fast = 10                 # time period for the fast EMA
K_fast = 2 / (num_periods_fast + 1)   # smoothing factor for fast EMA
ema_fast = 0
num_periods_slow = 40                 # time period for slow EMA
K_slow = 2 / (num_periods_slow + 1)   # smoothing factor for slow EMA
ema_slow = 0
ema_fast_values = []                  # we will hold fast EMA values for visualization purposes
ema_slow_values = []                  # we will hold slow EMA values for visualization purposes
apo_values = []                       # track computed absolute price oscillator values

for close_price in close:
  if ema_fast == 0:                   # first observation
    ema_fast = close_price
    ema_slow = close_price
  else:
    ema_fast = (close_price - ema_fast) * K_fast + ema_fast
    ema_slow = (close_price - ema_slow) * K_slow + ema_slow

  ema_fast_values.append(ema_fast)
  ema_slow_values.append(ema_slow)
  apo_values.append(ema_fast - ema_slow)

data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(FastExponential10DayMovingAverage=pd.Series(ema_fast_values, index=data.index))
data = data.assign(SlowExponential40DayMovingAverage=pd.Series(ema_slow_values, index=data.index))
data = data.assign(AbsolutePriceOscillator=pd.Series(apo_values, index=data.index))
print(data.tail(10))


### Charting
close_price = data['ClosePrice']
ema_f = data['FastExponential10DayMovingAverage']
ema_s = data['SlowExponential40DayMovingAverage']
apo = data['AbsolutePriceOscillator']

fig = plt.figure()
ax1 = fig.add_subplot(211, ylabel=f'{ticker} price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ema_f.plot(ax=ax1, color='b', lw=2., legend=True)
ema_s.plot(ax=ax1, color='r', lw=2., legend=True)
ax2 = fig.add_subplot(212, ylabel='APO')
apo.plot(ax=ax2, color='black', lw=2., legend=True)
plt.show()