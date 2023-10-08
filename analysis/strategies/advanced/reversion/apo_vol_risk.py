'''
Volatility adjusted mean reversion strategy (APO)
Including risk checks

We will adjust the number of days used in the Fast and Slow depending on the volatility (standard deviation),
making them more reactive to newer observations during periods of higher than normal volatility.

And use a volatility-adjusted APO entry/exit signal, making us less aggressive in entering positions during
periods of higher volatility, and more aggressive existing positions.
'''

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import matplotlib.pyplot as plt
from utils.data import load_financial_data
import statistics as stats
import math as math


### Get data
data = load_financial_data('GOOG', '2014-01-01', '2018-01-01', 'GOOG_data.pkl')


### Variable definitions
# variables for EMA Calculation
num_periods_fast = 10                 # time period for the fast EMA
K_fast = 2 / (num_periods_fast + 1)   # smoothing factor for fast EMA
ema_fast = 0
ema_fast_values = []                  # we will hold fast EMA values for visualization purposes
num_periods_slow = 40                 # time period for slow EMA
K_slow = 2 / (num_periods_slow + 1)   # smoothing factor for slow EMA
ema_slow = 0
ema_slow_values = []                  # we will hold slow EMA values for visualization purposes
apo_values = []                       # track computed APO value signals

# variables for trading strategy trade, position & pnl management
orders = []                           # for tracking buy/sell order, +1 for buy order, -1 for sell order, 0 for no-action
positions = []                        # for tracking positions, +ve for long positions, -ve for short positions, 0 for flat/no position
pnls = []                             # for tracking total_pnls
last_buy_price = 0                    # price at which last buy trade was made, used to prevent over-trading at/around the same price
last_sell_price = 0                   # price at which last sell trade was made, used to prevent over-trading at/around the same price
position = 0                          # current position of the trading strategy
buy_sum_price_qty = 0                 # summation of products of buy_trade_price and buy_trade_qty for every buy Trade made since last time being flat
buy_sum_qty = 0                       # summation of buy_trade_qty for every buy Trade made since last time being flat
sell_sum_price_qty = 0                # summation of products of sell_trade_price and sell_trade_qty for every sell Trade made since last time being flat
sell_sum_qty = 0                      # summation of sell_trade_qty for every sell Trade made since last time being flat
open_pnl = 0                          # open/Unrealized PnL marked to market
closed_pnl = 0                        # closed/Realized PnL so far

# variables that define strategy behavior/thresholds
APO_VALUE_FOR_BUY_ENTRY = -10         # APO trading signal value below which to enter buy-orders/long-position
APO_VALUE_FOR_SELL_ENTRY = 10         # APO trading signal value above which to enter sell-orders/short-position
MIN_PRICE_MOVE_FROM_LAST_TRADE = 10   # minimum price change since last trade before considering trading again, this is to prevent over-trading at/around same prices
NUM_SHARES_PER_TRADE = 10             # number of shares to buy/sell on every trade
MIN_PROFIT_TO_CLOSE = 10 * NUM_SHARES_PER_TRADE     # minimum Open/Unrealized profit at which to close positions and lock profits

# variables used to compute standard deviation as a volatility measure
SMA_NUM_PERIODS = 20                  # look back period
price_history = []                    # history of prices

# risk limits
RISK_ADJ = 1.5
RISK_LIMIT_WEEKLY_STOP_LOSS = -12000 * RISK_ADJ
RISK_LIMIT_MONTHLY_STOP_LOSS = -14000 * RISK_ADJ
RISK_LIMIT_MAX_POSITION = 250 * RISK_ADJ
RISK_LIMIT_MAX_POSITION_HOLDING_TIME_DAYS = 120 * RISK_ADJ
RISK_LIMIT_MAX_TRADE_SIZE = 10 * RISK_ADJ
RISK_LIMIT_MAX_TRADED_VOLUME = 4000 * RISK_ADJ

risk_violated = False
traded_volume = 0
current_pos = 0
current_pos_start = 0



### Algo logic
close = data["Close"]

for close_price in close:
    price_history.append(close_price)
    if len(price_history) > SMA_NUM_PERIODS:
        del (price_history[0])

    sma = stats.mean(price_history)
    variance = 0
    for price in price_history:
        variance = variance + ((price - sma) ** 2)

    stdev = math.sqrt(variance / len(price_history))
    stdev_factor = stdev / 15       # 15 was the average stdev seen in history
    if stdev_factor == 0:
        stdev_factor = 1

    if ema_fast == 0:
        ema_fast = close_price
        ema_slow = close_price
    else:
        ema_fast = (close_price - ema_fast) * (K_fast * stdev_factor) + ema_fast
        ema_slow = (close_price - ema_slow) * (K_slow * stdev_factor) + ema_slow

    ema_fast_values.append(ema_fast)
    ema_slow_values.append(ema_slow)
    apo = ema_fast - ema_slow
    apo_values.append(apo)

    # risk check
    if NUM_SHARES_PER_TRADE > RISK_LIMIT_MAX_TRADE_SIZE:
        print('RiskViolation -> NUM_SHARES_PER_TRADE(', NUM_SHARES_PER_TRADE, ') > RISK_LIMIT_MAX_TRADE_SIZE(', RISK_LIMIT_MAX_TRADE_SIZE), ')'
        risk_violated = True

    # sell conditions
    sell_cond1 = apo > (APO_VALUE_FOR_SELL_ENTRY * stdev_factor) and abs(close_price - last_sell_price) > (MIN_PRICE_MOVE_FROM_LAST_TRADE * stdev_factor)
    sell_cond2 = position > 0 and (apo >= 0 or open_pnl > (MIN_PROFIT_TO_CLOSE / stdev_factor))
    # buy conditions
    buy_cond1 = apo < (APO_VALUE_FOR_BUY_ENTRY * stdev_factor) and abs(close_price - last_buy_price) > (MIN_PRICE_MOVE_FROM_LAST_TRADE * stdev_factor)
    buy_cond2 = position < 0 and (apo <= 0 or open_pnl > (MIN_PROFIT_TO_CLOSE / stdev_factor))

    if not risk_violated and sell_cond1 or sell_cond2:
        orders.append(-1)
        last_sell_price = close_price
        position -= NUM_SHARES_PER_TRADE
        sell_sum_price_qty += (close_price * NUM_SHARES_PER_TRADE)
        sell_sum_qty += NUM_SHARES_PER_TRADE
        print("Sell " + str(NUM_SHARES_PER_TRADE) + " @ " + str(close_price) + " | Position: " + str(position))
    elif not risk_violated and buy_cond1 or buy_cond2:
        orders.append(+1)
        last_buy_price = close_price
        position += NUM_SHARES_PER_TRADE
        buy_sum_price_qty += (close_price * NUM_SHARES_PER_TRADE)
        buy_sum_qty += NUM_SHARES_PER_TRADE
        print("Buy " + str(NUM_SHARES_PER_TRADE) + " @ " + str(close_price) + " | Position: " + str(position))
    else:
        orders.append(0)

    positions.append(position)

    # risk checks
    if current_pos == 0:
        if position != 0:
            current_pos = position
            current_pos_start = len(positions)
    elif current_pos * position <= 0:
        current_pos = position
        position_holding_time = len(positions) - current_pos_start
        current_pos_start = len(positions)

        if position_holding_time > RISK_LIMIT_MAX_POSITION_HOLDING_TIME_DAYS:
            print('RiskViolation -> position_holding_time(',position_holding_time,') > RISK_LIMIT_MAX_POSITION_HOLDING_TIME_DAYS(',RISK_LIMIT_MAX_POSITION_HOLDING_TIME_DAYS,')')
            risk_violated = True

    if abs(position) > RISK_LIMIT_MAX_POSITION:
        print('RiskViolation -> position(',position,') > RISK_LIMIT_MAX_POSITION(',RISK_LIMIT_MAX_POSITION,')')
        risk_violated = True

    if traded_volume > RISK_LIMIT_MAX_TRADED_VOLUME:
        print('RiskViolation -> traded_volume(',traded_volume,') > RISK_LIMIT_MAX_TRADED_VOLUME(',RISK_LIMIT_MAX_TRADED_VOLUME,')')
        risk_violated = True

    # pnl
    open_pnl = 0
    if position > 0:
        if sell_sum_qty > 0:
            open_pnl = abs(sell_sum_qty) * (sell_sum_price_qty / sell_sum_qty - buy_sum_price_qty / buy_sum_qty)
        open_pnl += abs(sell_sum_qty - position) * (close_price - buy_sum_price_qty / buy_sum_qty)
    elif position < 0:
        if buy_sum_qty > 0:
            open_pnl = abs(buy_sum_qty) * (sell_sum_price_qty / sell_sum_qty - buy_sum_price_qty / buy_sum_qty)
        open_pnl += abs(buy_sum_qty - position) * (sell_sum_price_qty / sell_sum_qty - close_price)
    else:
        closed_pnl += (sell_sum_price_qty - buy_sum_price_qty)
        buy_sum_price_qty = 0
        buy_sum_qty = 0
        sell_sum_price_qty = 0
        sell_sum_qty = 0
        last_buy_price = 0
        last_sell_price = 0

    print("OpenPnL: " + str(open_pnl) + " | ClosedPnL: " + str(closed_pnl) + " | TotalPnL: " + str(open_pnl + closed_pnl))
    pnls.append(closed_pnl + open_pnl)

    # risk check
    if len(pnls) > 5:
        weekly_loss = pnls[-1] - pnls[-6]
        if weekly_loss < RISK_LIMIT_WEEKLY_STOP_LOSS:
            print('RiskViolation -> weekly_loss(',weekly_loss,') < RISK_LIMIT_WEEKLY_STOP_LOSS(',RISK_LIMIT_WEEKLY_STOP_LOSS,')')
            risk_violated = True

    if len(pnls) > 20:
        monthly_loss = pnls[-1] - pnls[-21]
        if monthly_loss < RISK_LIMIT_MONTHLY_STOP_LOSS:
            print('RiskViolation -> monthly_loss(',monthly_loss,') < RISK_LIMIT_MONTHLY_STOP_LOSS(',RISK_LIMIT_MONTHLY_STOP_LOSS,')')
            risk_violated = True


#### Charting
data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(Fast10DayEMA=pd.Series(ema_fast_values, index=data.index))
data = data.assign(Slow40DayEMA=pd.Series(ema_slow_values, index=data.index))
data = data.assign(APO=pd.Series(apo_values, index=data.index))
data = data.assign(Trades=pd.Series(orders, index=data.index))
data = data.assign(Position=pd.Series(positions, index=data.index))
data = data.assign(Pnl=pd.Series(pnls, index=data.index))
print(data.head(10))

data['ClosePrice'].plot(color='blue', lw=3., legend=True)
data['Fast10DayEMA'].plot(color='y', lw=1., legend=True)
data['Slow40DayEMA'].plot(color='m', lw=1., legend=True)
plt.plot(data.loc[data.Trades == 1].index, data.ClosePrice[data.Trades == 1], color='g', lw=0, marker='^', markersize=7, label='buy')
plt.plot(data.loc[data.Trades == -1].index, data.ClosePrice[data.Trades == -1], color='r', lw=0, marker='v', markersize=7, label='sell')
plt.legend()
plt.show()

data['APO'].plot(color='k', lw=3., legend=True)
plt.plot(data.loc[data.Trades == 1].index, data.APO[data.Trades == 1], color='g', lw=0, marker='^', markersize=7, label='buy')
plt.plot(data.loc[data.Trades == -1].index, data.APO[data.Trades == -1], color='r', lw=0, marker='v', markersize=7, label='sell')
plt.legend()
plt.show()

data['Position'].plot(color='k', lw=1., legend=True)
plt.plot(data.loc[data.Position == 0].index, data.Position[data.Position == 0], color='k', lw=0, marker='.', label='flat')
plt.plot(data.loc[data.Position > 0].index, data.Position[data.Position > 0], color='g', lw=0, marker='+', label='long')
plt.plot(data.loc[data.Position < 0].index, data.Position[data.Position < 0], color='r', lw=0, marker='_', label='short')
plt.legend()
plt.show()

data['Pnl'].plot(color='k', lw=1., legend=True)
plt.plot(data.loc[data.Pnl > 0].index, data.Pnl[data.Pnl > 0], color='g', lw=0, marker='+', label='profit')
plt.plot(data.loc[data.Pnl < 0].index, data.Pnl[data.Pnl < 0], color='r', lw=0, marker='_', label='loss')
plt.legend()
plt.show()

data_dir = '/Users/caolanraff/Development/projects/algo-trading/data/'
data.to_csv(data_dir + 'volatility_adjusted_mean_reversion.csv', sep=",")