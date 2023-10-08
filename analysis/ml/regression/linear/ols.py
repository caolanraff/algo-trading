'''
Ordinary Least Squares
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.data import load_financial_data
from ml.utils import create_regression_trading_condition, create_train_split_group
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score


### Get data
ticker = 'GOOG'
data = load_financial_data(ticker, '2001-01-01', '2018-01-01', 'GOOG_data_large.pkl')


### Build Model
data, X, Y = create_regression_trading_condition(data)

pd.plotting.scatter_matrix(data[['Open-Close', 'High-Low', 'Target']], grid=True, diagonal='kde')
plt.show()

X_train, X_test, Y_train, Y_test = create_train_split_group(X, Y, split_ratio=0.8)
model = linear_model.LinearRegression()
model.fit(X_train, Y_train)
print('Coefficients: \n', model.coef_)


### Test model
print('Mean squared error: %.2f' % mean_squared_error(Y_train, model.predict(X_train)))
print('Variance score: %.2f' % r2_score(Y_train, model.predict(X_train)))

print('Mean squared error: %.2f' % mean_squared_error(Y_test, model.predict(X_test)))
print('Variance score: %.2f' % r2_score(Y_test, model.predict(X_test)))


### Prediction
data['Predicted_Signal'] = model.predict(X)
data[ticker + '_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
data['Strategy_Returns'] = data['%s_Returns' % ticker] * data['Predicted_Signal'].shift(1)
print(data.tail(10))


### Charting
split_value = len(X_train)
cum_symbol_return = data[split_value:]['%s_Returns' % ticker].cumsum() * 100
cum_strategy_return = data[split_value:]['Strategy_Returns'].cumsum() * 100

plt.figure(figsize=(10, 5))
plt.plot(cum_symbol_return, label='%s Returns' % ticker)
plt.plot(cum_strategy_return, label='Strategy Returns')
plt.legend()
plt.show()


### Sharpe
strategy_std = cum_symbol_return.std()
sharpe = (cum_symbol_return - cum_strategy_return) / strategy_std
print('Sharpe: %s' % sharpe.mean())