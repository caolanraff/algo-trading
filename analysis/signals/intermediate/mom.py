'''
The Momentum (MOM) indicator compares the current price with the previous price from a selected number of periods ago.
This indicator is similar to the “Rate of Change” indicator, but the MOM does not normalize the price,
so different instruments can have different indicator values based on their point values.

MOM =  Price - Price of n periods ago
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
time_period = 20          # how far to look back to find reference price to compute momentum
history = []              # history of observed prices to use in momentum calculation
mom_values = []           # track momentum values for visualization purposes

for close_price in close:
  history.append(close_price)
  if len(history) > time_period:    # history is at most 'time_period' number of observations
    del (history[0])

  mom = close_price - history[0]
  mom_values.append(mom)

data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(MomentumFromPrice20DaysAgo=pd.Series(mom_values, index=data.index))
print(data.tail(10))


### Charting
close_price = data['ClosePrice']
mom = data['MomentumFromPrice20DaysAgo']

fig = plt.figure()
ax1 = fig.add_subplot(211, ylabel=f'{ticker} price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ax2 = fig.add_subplot(212, ylabel='Momentum in $')
mom.plot(ax=ax2, color='b', lw=2., legend=True)
plt.show()