"""
Act as a liquidity provider / exchange.
It will send price updates to the system.
Market data.
"""

from random import randrange, sample, seed


class LiquidityProvider:
    def __init__(self, lp_2_gw=None):  # lp_2_gw will be the channel to send price updates on
        self.orders = []
        self.order_id = 0
        seed(0)
        self.lp_2_gw = lp_2_gw

    def lookup_orders(self, id):
        count = 0
        for o in self.orders:
            if o['id'] == id:
                return o, count
            count += 1
        return None, None

    def insert_manual_order(self, order):
        if self.lp_2_gw is None:
            print('simulation mode')
            return order
        self.lp_2_gw.append(order.copy())

    def generate_random_order(self):
        price = randrange(8, 12)
        quantity = randrange(1, 10) * 100
        side = sample(['buy', 'sell'], 1)[0]
        order_id = randrange(0, self.order_id + 1)
        o = self.lookup_orders(order_id)

        new_order = False
        if o is None:
            action = 'new'
            new_order = True
        else:
            action = sample(['modify', 'delete'], 1)[0]

        ord = {
            'id': self.order_id,
            'price': price,
            'quantity': quantity,
            'side': side,
            'action': action
        }

        if not new_order:
            self.order_id += 1
            self.orders.append(ord)

        if not self.lp_2_gw:
            print('simulation mode')
            return ord
        self.lp_2_gw.append(ord.copy())
