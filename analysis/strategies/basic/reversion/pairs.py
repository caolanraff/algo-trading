'''
Pairs trading
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.data import load_financial_data
from statsmodels.tsa.stattools import coint
import seaborn

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

### Get data
tickers = ['SPY', 'AAPL', 'ADBE', 'LUV', 'MSFT', 'SKYW', 'QCOM', 'HPQ', 'JNPR', 'AMD', 'IBM']
data = load_financial_data(tickers, '2001-01-01', '2018-01-01', 'multi_data_large.pkl')


### Analysis
def find_cointegrated_pairs(data):
    n = data.shape[1]
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []

    for i in range(n):
        for j in range(i + 1, n):
            result = coint(data[keys[i]], data[keys[j]])
            pvalue_matrix[i, j] = result[1]
            if result[1] < 0.02:
                pairs.append((keys[i], keys[j]))

    return pvalue_matrix, pairs


pvalues, pairs = find_cointegrated_pairs(data['Adj Close'])

# if p-value is < 0.02, it means the symbols can be co-integrated
# this means that the two symbols will keep the same spread on average
seaborn.heatmap(pvalues, xticklabels=tickers, yticklabels=tickers, mask=(pvalues >= 0.98))
#plt.show()


### Algo logic (artificial symbols/prices)
np.random.seed(123)
symbol1_returns = np.random.normal(0, 1, 100)
symbol1_prices = pd.Series(np.cumsum(symbol1_returns), name='symbol1') + 10
noise = np.random.normal(0, 1, 100)
symbol2_prices = symbol1_prices + 10 + noise
plt.clf()
plt.title("symbol1 and symbol2 prices")
symbol1_prices.plot()
symbol2_prices.plot()
#plt.show()

score, pvalue, _ = coint(symbol1_prices, symbol2_prices)
print(pvalue)

ratios = symbol1_prices / symbol2_prices
plt.clf()
plt.title("Ratio between Symbol 1 and Symbol 2 price")
ratios.plot()
#plt.show()

# zscore returns how far a piece of data is from the population mean
def zscore(series):
    return (series - series.mean()) / np.std(series)


# every time the z-score reaches one of the thresholds, we have a trading signal
plt.clf()
zscore(ratios).plot()
plt.title("Z-score evolution")
plt.axhline(zscore(ratios).mean(), color="black")
plt.axhline(1.0, color="red")
plt.axhline(-1.0, color="green")
#plt.show()

# adding trading signals
symbol1_buy = symbol1_prices.copy()
symbol1_sell = symbol1_prices.copy()
symbol2_buy = symbol2_prices.copy()
symbol2_sell = symbol2_prices.copy()

plt.clf()
symbol1_prices.plot()
symbol1_buy[zscore(ratios) > -1] = 0
symbol1_sell[zscore(ratios) < 1] = 0
symbol1_buy.plot(color="g", linestyle="None", marker="^")
symbol1_sell.plot(color="r", linestyle="None", marker="v")

symbol2_prices.plot()
symbol2_buy[zscore(ratios) < 1] = 0
symbol2_sell[zscore(ratios) > -1] = 0
symbol2_buy.plot(color="g", linestyle="None", marker="^")
symbol2_sell.plot(color="r", linestyle="None", marker="v")

x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, symbol1_prices.min(), symbol2_prices.max()))
plt.legend(["Symbol1", "Buy Signal", "Sell Signal", "Symbol2"])
#plt.show()


### Algo logic (real symbols/prices)
symbol1_prices = data["Adj Close"]["MSFT"]
symbol2_prices = data["Adj Close"]["JNPR"]
plt.clf()
symbol1_prices.plot()
symbol2_prices.plot()
plt.title("MSFT and JNPR prices")
plt.legend()
plt.show()

# adding trading signals
symbol1_buy = symbol1_prices.copy()
symbol1_sell = symbol1_prices.copy()
symbol2_buy = symbol2_prices.copy()
symbol2_sell = symbol2_prices.copy()
ratios = symbol1_prices / symbol2_prices

plt.clf()
symbol1_prices.plot()
symbol1_buy[zscore(ratios) > -1] = 0
symbol1_sell[zscore(ratios) < 1] = 0
symbol1_buy.plot(color="g", linestyle="None", marker="^")
symbol1_sell.plot(color="r", linestyle="None", marker="v")

symbol2_prices.plot()
symbol2_buy[zscore(ratios) < 1] = 0
symbol2_sell[zscore(ratios) > -1] = 0
symbol2_buy.plot(color="g", linestyle="None", marker="^")
symbol2_sell.plot(color="r", linestyle="None", marker="v")

x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, symbol1_prices.min(), symbol2_prices.max()))
plt.legend(["Symbol1", "Buy Signal", "Sell Signal", "Symbol2"])
plt.show()

# note: if placing too many orders, can set a higher z-score threshold
# the above are signals when to enter a position, to exit a position the z-score should be within the thresholds


### Strategy
strategy = pd.DataFrame(index=symbol1_prices.index)
strategy['symbol1_price'] = symbol1_prices
cnt = len(symbol1_prices)
strategy['symbol1_buy'] = np.zeros(cnt)
strategy['symbol1_sell'] = np.zeros(cnt)
strategy['symbol2_buy'] = np.zeros(cnt)
strategy['symbol2_sell'] = np.zeros(cnt)
strategy['delta'] = np.zeros(cnt)


position = 0            # max open position can be 1
s1_shares = 1000000     # used to ensure same notional for both symbols

for i in range(cnt):
    s1_position = symbol1_prices[i] * s1_shares
    s2_position = symbol2_prices[i] * int(s1_position / symbol2_prices[i])
    delta = s1_position - s2_position
    if position == 0 and symbol1_buy[i] != 0:
        strategy['symbol1_buy'][i] = s1_position
        strategy['symbol2_sell'][i] = s2_position
        strategy['delta'][i] = delta
        position = 1
    elif position == 0 and symbol1_sell[i] != 0:
        strategy['symbol1_sell'][i] = s1_position
        strategy['symbol2_buy'][i] = s2_position
        strategy['delta'][i] = delta
        position = -1
    elif position == -1 and (symbol1_sell[i] == 0 or i == cnt - 1):
        strategy['symbol1_buy'][i] = s1_position
        strategy['symbol2_sell'][i] = s2_position
        position = 0
    elif position == 1 and (symbol1_buy[i] == 0 or i == cnt - 1):
        strategy['symbol1_sell'][i] = s1_position
        strategy['symbol2_buy'][i] = s2_position
        position = 0


print(strategy.head(10))

plt.clf()
symbol1_prices.plot()
strategy['symbol1_buy'].plot(color="g", linestyle="None", marker="^")
strategy['symbol1_sell'].plot(color="r", linestyle="None", marker="v")
symbol2_prices.plot()
strategy['symbol2_buy'].plot(color="g", linestyle="None", marker="^")
strategy['symbol2_sell'].plot(color="r", linestyle="None", marker="v")
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, symbol1_prices.min(), symbol2_prices.max()))
plt.legend(["Symbol1", "Buy Signal", "Sell Signal", "Symbol2"])
plt.show()


### position
plt.clf()
strategy['symbol1_position'] = strategy['symbol1_buy'] - strategy['symbol1_sell']
strategy['symbol2_position'] = strategy['symbol2_buy'] - strategy['symbol2_sell']
strategy['symbol1_position'].cumsum().plot()
strategy['symbol2_position'].cumsum().plot()
strategy['total_position'] = strategy['symbol1_position'] + strategy['symbol2_position']
strategy['total_position'].cumsum().plot()
plt.title("Symbol 1 and Symbol 2 position")
plt.legend()
plt.show()


plt.clf()
strategy['delta'].plot()
plt.title("Delta Position")
plt.show()