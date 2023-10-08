'''
Like any other retail products, financial products follow trends and seasonality during different seasons.
There are multiple seasonality effects: weekend, monthly, and holidays.
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from utils.data import load_financial_data


### Get data
start_date = '2001-01-01'
end_date = '2018-01-01'
ticker = 'GOOG'
SRC_DATA_FILENAME = ticker + '_data_large.pkl'

data = load_financial_data(ticker, start_date, end_date, SRC_DATA_FILENAME)
monthly_return = data['Adj Close'].pct_change().groupby(
    [data['Adj Close'].index.year,
     data['Adj Close'].index.month]).mean()


### Algo logic
monthly_return_list = []

for i in range(len(monthly_return)):
    monthly_return_list.append({'month': monthly_return.index[i][1],
                                'monthly_return': monthly_return.iloc[i]})

monthly_return_df = pd.DataFrame(monthly_return_list, columns=('month', 'monthly_return'))


### Charting
monthly_return_df.boxplot(column='monthly_return', by='month')
ax = plt.gca()
labels = [item.get_text() for item in ax.get_xticklabels()]
labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ax.set_xticklabels(labels)
ax.set_ylabel(f'{ticker} return')
plt.tick_params(axis='both', which='major', labelsize=7)
plt.title(f"{ticker} Monthly return 2001-2018")
plt.suptitle("")
plt.show()


# Displaying rolling statistics
def plot_rolling_statistics_ts(ts, titletext, ytext, window_size=12):
    ts.plot(color='red', label='Original', lw=0.5)
    ts.rolling(window_size).mean().plot(color='blue', label='Rolling Mean')
    ts.rolling(window_size).std().plot(color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.ylabel(ytext)
    plt.title(titletext)
    plt.show()

plot_rolling_statistics_ts(data['Adj Close'], f'{ticker} prices rolling mean and standard deviation', 'Daily prices', 365)
plot_rolling_statistics_ts(monthly_return[1:], f'{ticker} prices rolling mean and standard deviation', 'Monthly return')
plot_rolling_statistics_ts(data['Adj Close']-data['Adj Close'].rolling(365).mean(), f'{ticker} prices without trend', 'Daily prices', 365)


# Use the Dickey-Fuller test to determine whether the timeseries is stationary
def test_stationarity(timeseries):
    print('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries[1:], autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    print(dfoutput)

test_stationarity(data['Adj Close'])    # returns a p-value of 0.99, therefore timeseries is not stationary
test_stationarity(monthly_return[1:])   # returns a p-value less than 0.05, therefore cannot say that the timeseries is not stationary


### Forecasting
# Auto-Regression Integrated Moving Averages (ARIMA) model
plt.figure()
plt.subplot(211)
plot_acf(monthly_return[1:], ax=plt.gca(), lags=10)     # autocorrelation function
plt.subplot(212)
plot_pacf(monthly_return[1:], ax=plt.gca(), lags=10)    # partial autocorrelation function
plt.show()

model = ARIMA(monthly_return.values[1:], order=(2, 0, 2))
fitted_results = model.fit()
monthly_return[1:].plot()
pd.Series(fitted_results.fittedvalues).plot(color='red')
plt.show()