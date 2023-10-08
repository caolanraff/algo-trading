"""
Event based backtester for the dual moving average strategy.

There is paper trading and live trading mode.
Paper trading implies that every time the strategy sends an order, it is filled at the price asked.
"""

import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

from collections import deque
import matplotlib.pyplot as plt

from src.liquidity_provider import LiquidityProvider
from src.market_simulator import MarketSimulator
from src.order_manager import OrderManager
from src.orderbook import OrderBook
from trading_strategy_dualMA import TradingStrategyDualMA
from utils.data import load_financial_data


data = load_financial_data('GOOG', '2001-01-01', '2018-01-01', 'goog_data.pkl')


def call_if_not_empty(deq, fun):
    while len(deq) > 0:
        fun()

class EventBasedBackTester:
    def __init__(self):
        self.lp_2_gw = deque()
        self.ob_2_ts = deque()
        self.ts_2_om = deque()
        self.ms_2_om = deque()
        self.om_2_ts = deque()
        self.gw_2_om = deque()
        self.om_2_gw = deque()

        self.lp = LiquidityProvider(self.lp_2_gw)
        self.ob = OrderBook(self.lp_2_gw, self.ob_2_ts)
        self.ts = TradingStrategyDualMA(self.ob_2_ts, self.ts_2_om, self.om_2_ts)
        self.ms = MarketSimulator(self.om_2_gw, self.gw_2_om)
        self.om = OrderManager(self.ts_2_om, self.om_2_ts, self.om_2_gw, self.gw_2_om)

    def process_data_from_yahoo(self, price):
        bid = {
            'id': 1,
            'price': price,
            'quantity': 1000,
            'side': 'bid',
            'action': 'new'
        }
        ask = {
            'id': 1,
            'price': price,
            'quantity': 1000,
            'side': 'ask',
            'action': 'new'
        }
        self.lp_2_gw.append(ask)
        self.lp_2_gw.append(bid)
        self.process_events()
        ask['action'] = 'delete'
        bid['action'] = 'delete'
        self.lp_2_gw.append(ask)
        self.lp_2_gw.append(bid)

    def process_events(self):
        while len(self.lp_2_gw) > 0:
            call_if_not_empty(self.lp_2_gw, self.ob.handle_order_from_gateway)
            call_if_not_empty(self.ob_2_ts, self.ts.handle_input_from_bb)
            call_if_not_empty(self.ts_2_om, self.om.handle_input_from_ts)
            call_if_not_empty(self.om_2_gw, self.ms.handle_order_from_gw)
            call_if_not_empty(self.gw_2_om, self.om.handle_input_from_market)
            call_if_not_empty(self.om_2_ts, self.ts.handle_response_from_om)


eb = EventBasedBackTester()

for i in zip(data.index, data['Adj Close']):
    price_information = {'date': i[0], 'price': float(i[1])}
    eb.process_data_from_yahoo(price_information['price'])
    eb.process_events()


plt.plot(eb.ts.list_paper_total, label="Paper Trading using Event-Based BackTester")
plt.plot(eb.ts.list_total, label="Trading using Event-Based BackTester")
plt.legend()
plt.show()
