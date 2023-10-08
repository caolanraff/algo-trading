'''
Statistical Arbitrage strategies is similar to pairs trading, but instead often has portfolios of hundreds of trading instruments,
whether they are futures, equities, options or currencies.
They also have a mixture of mean reversion and trend following strategies.

e.g the price of an instrument has a larger deviation than expected from a basket of instruments.
note that lead-lag needs to be considered.
'''

import sys

start_date = '2014-01-01'
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import pandas as pd
import matplotlib.pyplot as plt
from utils.data import load_financial_data
import numpy as np
from itertools import cycle
import statistics as stats


### Get data
trading_instrument = 'CADUSD=X'
symbols = ['AUDUSD=X', 'GBPUSD=X', 'CADUSD=X', 'CHFUSD=X', 'EURUSD=X', 'JPYUSD=X', 'NZDUSD=X']
start_date = '2014-01-01'
end_date = '2018-01-01'

symbols_data = {}
for i in symbols:
    symbols_data[i] = load_financial_data(i, start_date, end_date, i + '_data.pkl')


### Visualise prices
cycol = cycle('bgrcmky')
price_data = pd.DataFrame()

for i in symbols:
    multiplier = 1.0
    if i == 'JPYUSD=X':
        multiplier = 100.0      # scaling

    label = i + ' Close Price'
    price_data = price_data.assign(label=pd.Series(symbols_data[i]['Close'] * multiplier, index=symbols_data[i].index))
    ax = price_data['label'].plot(color=next(cycol), lw=2., label=label)


plt.xlabel('Date')
plt.ylabel('Scaled Price')
plt.legend()
plt.show()


# Variables that are used to compute simple moving average and price deviation from simple moving average
SMA_NUM_PERIODS = 20                # look back period
price_history = {}                  # history of prices
PRICE_DEV_NUM_PRICES = 200          # look back period of ClosePrice deviations from SMA
price_deviation_from_sma = {}       # history of ClosePrice deviations from SMA

# We will use this to iterate over all the days of data we have
num_days = len(symbols_data[trading_instrument].index)
correlation_history = {}            # history of correlations per currency pair
delta_projected_actual_history = {} # history of differences between Projected ClosePrice deviation and actual ClosePrice deviation per currency pair
final_delta_projected_history = []  # history of differences between final Projected ClosePrice deviation for TRADING_INSTRUMENT and actual ClosePrice deviation

# Variables for Trading Strategy trade, position & pnl management:
orders = []                         # Container for tracking buy/sell order, +1 for buy order, -1 for sell order, 0 for no-action
positions = []                      # Container for tracking positions, +ve for long positions, -ve for short positions, 0 for flat/no position
pnls = []                           # Container for tracking total_pnls, this is the sum of closed_pnl i.e. pnls already locked in and open_pnl i.e. pnls for open-position marked to market price
last_buy_price = 0                  # Price at which last buy trade was made, used to prevent over-trading at/around the same price
last_sell_price = 0                 # Price at which last sell trade was made, used to prevent over-trading at/around the same price
position = 0                        # Current position of the trading strategy
buy_sum_price_qty = 0               # Summation of products of buy_trade_price and buy_trade_qty for every buy Trade made since last time being flat
buy_sum_qty = 0                     # Summation of buy_trade_qty for every buy Trade made since last time being flat
sell_sum_price_qty = 0              # Summation of products of sell_trade_price and sell_trade_qty for every sell Trade made since last time being flat
sell_sum_qty = 0                    # Summation of sell_trade_qty for every sell Trade made since last time being flat
open_pnl = 0                        # Open/Unrealized PnL marked to market
closed_pnl = 0                      # Closed/Realized PnL so far

# Variables that define strategy behavior/thresholds
VALUE_FOR_BUY_ENTRY = 0.01          # StatArb trading signal value aboe which to enter buy-orders/long-position
VALUE_FOR_SELL_ENTRY = -0.01        # StatArb trading signal value below which to enter sell-orders/short-position
MIN_PRICE_MOVE_FROM_LAST_TRADE = 0.01   # Minimum price change since last trade before considering trading again, this is to prevent over-trading at/around same prices
NUM_SHARES_PER_TRADE = 1000000      # Number of currency to buy/sell on every trade
MIN_PROFIT_TO_CLOSE = 10            # Minimum Open/Unrealized profit at which to close positions and lock profits


for i in range(0, num_days):
    close_prices = {}

    # build close price series, compute sma for each symbol and price deviation from sma
    for s in symbols:
        close_prices[s] = symbols_data[s]['Close'].iloc[i]
        if not s in price_history.keys():
            price_history[s] = []
            price_deviation_from_sma[s] = []

        price_history[s].append(close_prices[s])
        if len(price_history[s]) > SMA_NUM_PERIODS:
            del (price_history[s][0])

        sma = stats.mean(price_history[s])
        price_deviation_from_sma[s].append(close_prices[s] - sma)
        if len(price_deviation_from_sma[s]) > PRICE_DEV_NUM_PRICES:
            del (price_deviation_from_sma[s][0])

        # compute covariance and correlation between trading instrument and every other symbol
    projected_dev_from_sma_using = {}
    for s in symbols:
        if s == trading_instrument:
             continue

        correlation_label = trading_instrument + '<-' + s
        if correlation_label not in correlation_history.keys():
            correlation_history[correlation_label] = []
            delta_projected_actual_history[correlation_label] = []

        if len(price_deviation_from_sma[s]) < 2:    # need at least 2 observations to compute correlation
            correlation_history[correlation_label].append(0)
            delta_projected_actual_history[correlation_label].append(0)
            continue

        corr = np.corrcoef(price_deviation_from_sma[trading_instrument], price_deviation_from_sma[s])
        cov = np.cov(price_deviation_from_sma[trading_instrument], price_deviation_from_sma[s])
        corr_trading_instrument_lead_instrument = corr[0, 1]
        cov_trading_instrument_lead_instrument = cov[0, 0] / cov[0, 1]
        correlation_history[correlation_label].append(corr_trading_instrument_lead_instrument)

        # projected price deviation in trading instrument
        projected_dev_from_sma_using[s] = price_deviation_from_sma[s][-1] * cov_trading_instrument_lead_instrument
        # delta +ve => signal says trading instrument price should have moved up more than what it did
        # delta -ve => signal says trading instrument price should have moved down more than what it did
        delta_projected_actual = (projected_dev_from_sma_using[s] - price_deviation_from_sma[trading_instrument][-1])
        delta_projected_actual_history[correlation_label].append(delta_projected_actual)

    # weigh predictions from each pair, weight is the correlation between those pairs
    sum_weights = 0
    for s in symbols:
        if s == trading_instrument:
            continue

        correlation_label = trading_instrument + '<-' + s
        sum_weights += abs(correlation_history[correlation_label][-1])

    final_delta_projected = 0
    close_price = close_prices[trading_instrument]
    for s in symbols:
        if s == trading_instrument:
            continue

        correlation_label = trading_instrument + '<-' + s
        final_delta_projected += abs(correlation_history[correlation_label][-1]) * delta_projected_actual_history[correlation_label][-1]

    if sum_weights != 0:
        final_delta_projected /= sum_weights
    else:
        final_delta_projected = 0

    final_delta_projected_history.append(final_delta_projected)

    # sell conditions
    sell_cond1 = (final_delta_projected < VALUE_FOR_SELL_ENTRY) and abs(close_price - last_sell_price) > MIN_PRICE_MOVE_FROM_LAST_TRADE
    sell_cond2 = (position > 0) and (open_pnl > MIN_PROFIT_TO_CLOSE)
    # buy conditions
    buy_cond1 = (final_delta_projected > VALUE_FOR_BUY_ENTRY) and abs(close_price - last_buy_price) > MIN_PRICE_MOVE_FROM_LAST_TRADE
    buy_cond2 = (position < 0) and (open_pnl > MIN_PROFIT_TO_CLOSE)

    if sell_cond1 or sell_cond2:
        orders.append(-1)
        last_sell_price = close_price
        position -= NUM_SHARES_PER_TRADE
        sell_sum_price_qty += (close_price * NUM_SHARES_PER_TRADE)
        sell_sum_qty += NUM_SHARES_PER_TRADE
        print("Sell ", NUM_SHARES_PER_TRADE, " @ ", close_price, "Position: ", position)
        print("OpenPnL: ", open_pnl, " ClosedPnL: ", closed_pnl, " TotalPnL: ", (open_pnl + closed_pnl))
    elif buy_cond1 or buy_cond2:
        orders.append(+1)
        last_buy_price = close_price
        position += NUM_SHARES_PER_TRADE
        buy_sum_price_qty += (close_price * NUM_SHARES_PER_TRADE)
        buy_sum_qty += NUM_SHARES_PER_TRADE
        print("Buy ", NUM_SHARES_PER_TRADE, " @ ", close_price, "Position: ", position)
        print("OpenPnL: ", open_pnl, " ClosedPnL: ", closed_pnl, " TotalPnL: ", (open_pnl + closed_pnl))
    else:
        orders.append(0)

    positions.append(position)

    # this section updates open/unrealised & closed/realised positions
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

    pnls.append(closed_pnl + open_pnl)


### strategy analysis
# plot correlations between trading instrument and other currency pairs
correlation_data = pd.DataFrame()
for s in symbols:
    if s == trading_instrument:
        continue

    correlation_label = trading_instrument + '<-' + s
    correlation_data = correlation_data.assign(label=pd.Series(correlation_history[correlation_label], index=symbols_data[s].index))
    ax = correlation_data['label'].plot(color=next(cycol), lw=2., label='Correlation ' + correlation_label)

plt.legend()
plt.show()

# plot StatArb signal provided by each currency pair
delta_projected_actual_data = pd.DataFrame()
for s in symbols:
    if s == trading_instrument:
        continue

    projection_label = trading_instrument + '<-' + s
    delta_projected_actual_data = delta_projected_actual_data.assign(StatArbTradingSignal=pd.Series(delta_projected_actual_history[projection_label], index=symbols_data[trading_instrument].index))
    ax = delta_projected_actual_data['StatArbTradingSignal'].plot(color=next(cycol), lw=1., label='StatArbTradingSignal ' + projection_label)

plt.legend()
plt.show()


delta_projected_actual_data = delta_projected_actual_data.assign(ClosePrice=pd.Series(symbols_data[trading_instrument]['Close'], index=symbols_data[trading_instrument].index))
delta_projected_actual_data = delta_projected_actual_data.assign(FinalStatArbTradingSignal=pd.Series(final_delta_projected_history, index=symbols_data[trading_instrument].index))
delta_projected_actual_data = delta_projected_actual_data.assign(Trades=pd.Series(orders, index=symbols_data[trading_instrument].index))
delta_projected_actual_data = delta_projected_actual_data.assign(Position=pd.Series(positions, index=symbols_data[trading_instrument].index))
delta_projected_actual_data = delta_projected_actual_data.assign(Pnl=pd.Series(pnls, index=symbols_data[trading_instrument].index))

# plot buy and sell trades
plt.plot(delta_projected_actual_data.index, delta_projected_actual_data.ClosePrice, color='k', lw=1., label='ClosePrice')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Trades == 1].index, delta_projected_actual_data.ClosePrice[delta_projected_actual_data.Trades == 1], color='r', lw=0, marker='^', markersize=7, label='buy')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Trades == -1].index, delta_projected_actual_data.ClosePrice[delta_projected_actual_data.Trades == -1], color='g', lw=0, marker='v', markersize=7, label='sell')
plt.legend()
plt.show()

# plot final trading signal
plt.plot(delta_projected_actual_data.index, delta_projected_actual_data.FinalStatArbTradingSignal, color='k', lw=1., label='FinalStatArbTradingSignal')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Trades == 1].index, delta_projected_actual_data.FinalStatArbTradingSignal[delta_projected_actual_data.Trades == 1], color='r', lw=0, marker='^', markersize=7, label='buy')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Trades == -1].index, delta_projected_actual_data.FinalStatArbTradingSignal[delta_projected_actual_data.Trades == -1], color='g', lw=0, marker='v', markersize=7, label='sell')
plt.legend()
plt.show()

# plot positions
plt.plot(delta_projected_actual_data.index, delta_projected_actual_data.Position, color='k', lw=1., label='Position')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Position == 0].index, delta_projected_actual_data.Position[delta_projected_actual_data.Position == 0], color='k', lw=0, marker='.', label='flat')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Position > 0].index, delta_projected_actual_data.Position[delta_projected_actual_data.Position > 0], color='r', lw=0, marker='+', label='long')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Position < 0].index, delta_projected_actual_data.Position[delta_projected_actual_data.Position < 0], color='g', lw=0, marker='_', label='short')
plt.legend()
plt.show()

# plot PnL
plt.plot(delta_projected_actual_data.index, delta_projected_actual_data.Pnl, color='k', lw=1., label='Pnl')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Pnl > 0].index, delta_projected_actual_data.Pnl[delta_projected_actual_data.Pnl > 0], color='g', lw=0, marker='.')
plt.plot(delta_projected_actual_data.loc[delta_projected_actual_data.Pnl < 0].index, delta_projected_actual_data.Pnl[delta_projected_actual_data.Pnl < 0], color='r', lw=0, marker='.')
plt.legend()
plt.show()