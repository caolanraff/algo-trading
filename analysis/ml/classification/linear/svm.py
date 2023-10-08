'''
Support Vector Machine
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.data import load_financial_data
from ml.utils import create_classification_trading_condition, create_train_split_group
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


### Get data
ticker = 'GOOG'
data = load_financial_data(ticker, '2001-01-01', '2018-01-01', 'GOOG_data_large.pkl')


### Training and testing data
data, X, Y = create_classification_trading_condition(data)
X_train, X_test, Y_train, Y_test = create_train_split_group(X, Y, split_ratio=0.8)


### Fit the model
model = SVC()
model.fit(X_train, Y_train)

accuracy_train = accuracy_score(Y_train, model.predict(X_train))
accuracy_test = accuracy_score(Y_test, model.predict(X_test))
print(accuracy_train, accuracy_test)


### Prediction
data['Predicted_Signal'] = model.predict(X)
data['%s_Returns' % ticker] = np.log(data['Close'] / data['Close'].shift(1))
data['Strategy_Returns'] = data['%s_Returns' % ticker] * data['Predicted_Signal'].shift(1)


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