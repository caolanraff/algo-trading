import pandas as pd
import matplotlib.pyplot as plt
from statistics import stdev, mean

data_dir = '/Users/caolanraff/Development/projects/algo-trading/data/'
results = pd.read_csv(data_dir + 'volatility_adjusted_mean_reversion.csv')
results = results[['Date', 'High', 'Low', 'ClosePrice', 'Trades', 'Position', 'Pnl']]
print(results.head())


### stop loss
# maximum amount of money strategy is allowed to use within certain timeframe
num_days = len(results.index)
pnl = results['Pnl']
weekly_losses = []
monthly_losses = []

for i in range(0, num_days):
    if i >= 5 and pnl[i - 5] > pnl[i]:
        weekly_losses.append(pnl[i] - pnl[i - 5])

    if i >= 20 and pnl[i - 20] > pnl[i]:
        monthly_losses.append(pnl[i] - pnl[i - 20])

plt.hist(weekly_losses, 50)
plt.gca().set(title='Weekly Loss Distribution', xlabel='$', ylabel='Frequency')
plt.show()

plt.hist(monthly_losses, 50)
plt.gca().set(title='Monthly Loss Distribution', xlabel='$', ylabel='Frequency')
plt.show()

# from these observations we can see that anything more than a 4k loss in a week, or 6k loss in a month is unexpected.

### max drawdown
# maximum loss that a strategy can take over a series of days
# peak to trough decline in a trading strategys account value
max_pnl = 0
max_drawdown = 0
drawdown_max_pnl = 0
drawdown_min_pnl = 0

for i in range(0, num_days):
    max_pnl = max(max_pnl, pnl[i])
    drawdown = max_pnl - pnl[i]

    if drawdown > max_drawdown:
        max_drawdown = drawdown
        drawdown_max_pnl = max_pnl
        drawdown_min_pnl = pnl[i]

print('Max Drawdown:', max_drawdown)

results['Pnl'].plot(x='Date', legend=True)
plt.axhline(y=drawdown_max_pnl, color='g')
plt.axhline(y=drawdown_min_pnl, color='r')
plt.show()


### position limits
# maximum position strategy can have at any 1 time
position = results['Position']
plt.hist(position, 20)
plt.gca().set(title='Position Distribution', xlabel='Shares', ylabel='Frequency')
plt.show()


### position holding time
position_holding_times = []
current_pos = 0
current_pos_start = 0

for i in range(0, num_days):
    pos = results['Position'].iloc[i]

    # flat and starting a new position
    if current_pos == 0:
        if pos != 0:
            current_pos = pos
            current_pos_start = i
        continue

    # going from long position to flat or short position or
    # going from short position to flat or long position
    if current_pos * pos <= 0:
        current_pos = pos
        position_holding_times.append(i - current_pos_start)
        current_pos_start = i

print(position_holding_times)
plt.hist(position_holding_times, 100)
plt.gca().set(title='Position Holding Time Distribution', xlabel='Holding time days', ylabel='Frequency')
plt.show()


### variance of PnLs
# measure how much PnLs vary day to day
# if large swings in PnL, its very volatile strategy
last_week = 0
weekly_pnls = []
weekly_losses = []

for i in range(0, num_days):
    if i - last_week >= 5:
        pnl_change = pnl[i] - pnl[last_week]
        weekly_pnls.append(pnl_change)
        if pnl_change < 0:
            weekly_losses.append(pnl_change)
        last_week = i

print('PnL Standard Deviation:', stdev(weekly_pnls))

plt.hist(weekly_pnls, 50)
plt.gca().set(title='Weekly PnL Distribution', xlabel='$', ylabel='Frequency')
plt.show()


### Sharpe & Sortino ratio
# very commonly used performance and risk metric to measure and compare strategies
# a similar performance/risk measure is sortino ratio, which only uses observations where strategy loses money
sharpe_ratio = mean(weekly_pnls) / stdev(weekly_pnls)
sortino_ratio = mean(weekly_pnls) / stdev(weekly_losses)

print('Sharpe ratio:', sharpe_ratio)
print('Sortino ratio:', sortino_ratio)


### Maximum executions per period
# max number of trades allowed per timeframe, stop over trading
executions_this_week = 0
executions_per_week = []
last_week = 0

for i in range(0, num_days):
    if results['Trades'].iloc[i] != 0:
        executions_this_week += 1

    if i - last_week >= 5:
        executions_per_week.append(executions_this_week)
        executions_this_week = 0
        last_week = i

plt.hist(executions_per_week, 10)
plt.gca().set(title='Weekly number of executions Distribution', xlabel='Number of executions', ylabel='Frequency')
plt.show()

executions_this_month = 0
executions_per_month = []
last_month = 0

for i in range(0, num_days):
    if results['Trades'].iloc[i] != 0:
        executions_this_month += 1

    if i - last_month >= 20:
        executions_per_month.append(executions_this_month)
        executions_this_month = 0
        last_month = i

plt.hist(executions_per_month, 20)
plt.gca().set(title='Monthly number of executions Distribution', xlabel='Number of executions', ylabel='Frequency')
plt.show()


### maximum trade size


### volume limits
traded_volume = 0

for i in range(0, num_days):
    if results['Trades'].iloc[i] != 0:
        traded_volume += abs(results['Position'].iloc[i] - results['Position'].iloc[i-1])

print('Total traded volume:', traded_volume)