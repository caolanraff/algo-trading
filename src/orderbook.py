

class OrderBook:
    def __init__(self, gt_2_ob=None, ob_to_ts=None):
        self.list_asks = []
        self.list_bids = []
        self.gw_2_ob = gt_2_ob
        self.ob_to_ts = ob_to_ts
        self.current_bid = None
        self.current_ask = None

    def handle_order_from_gateway(self, order=None):
        if self.gw_2_ob is None:
            print('simulation mode')
            self.handle_order(order)
        elif len(self.gw_2_ob) > 0:
            order_from_gw = self.gw_2_ob.popleft()
            self.handle_order(order_from_gw)

    def handle_order(self, order):
        if order['action'] == 'new':
            self.handle_new(order)
        elif order['action'] == 'modify':
            self.handle_modify(order)
        elif order['action'] == 'delete':
            self.handle_delete(order)
        else:
            print('[ERROR] cannot handle this action')
        return self.check_generate_top_of_book_event()

    def handle_new(self, order):
        if order['side'] == 'bid':
            self.list_bids.append(order)
            self.list_bids.sort(key=lambda x: x['price'], reverse=True)
        elif order['side'] == 'ask':
            self.list_asks.append(order)
            self.list_asks.sort(key=lambda x: x['price'])

    def handle_modify(self, order):
        o = self.find_order_in_a_list(order)
        if o['quantity'] > order['quantity']:
            o['quantity'] = order['quantity']
        else:
            print('[ERROR] incorrect size')
        return None

    def handle_delete(self, order):
        lookup_list = self.get_list(order)
        o = self.find_order_in_a_list(order, lookup_list)
        if o is not None:
            lookup_list.remove(o)
        return None

    def get_list(self, order):
        if 'side' in order:
            if order['side'] == 'bid':
                lookup_list = self.list_bids
            elif order['side'] == 'ask':
                lookup_list = self.list_asks
            else:
                print('[ERROR] incorrect side')
                return None
            return lookup_list
        else:
            for o in self.list_bids:
                if o['id'] == order['id']:
                    return self.list_bids
            for o in self.list_asks:
                if o['id'] == order['id']:
                    return self.list_asks
            return None

    def find_order_in_a_list(self, order, lookup_list=None):
        if lookup_list is None:
            lookup_list = self.get_list(order)
        if lookup_list is not None:
            for o in lookup_list:
                if o['id'] == order['id']:
                    return o
            print('[ERROR] order not found id=%d' % (order['id']))
        return None

    def create_book_event(self, bid, ask):
        book_event = {
            "bid_price": bid['price'] if bid else -1,
            "bid_quantity": bid['quantity'] if bid else -1,
            "offer_price": ask['price'] if ask else -1,
            "offer_quantity": ask['quantity'] if ask else -1
        }
        return book_event

    def check_generate_top_of_book_event(self):
        tob_changed = False

        if len(self.list_bids) == 0:
            if self.current_bid is not None:
                tob_changed = True
        else:
            if self.current_bid != self.list_bids[0]:
                tob_changed = True
                self.current_bid = self.list_bids[0]

        if len(self.list_asks) == 0:
            if self.current_ask is not None:
                tob_changed = True
        else:
            if self.current_ask != self.list_asks[0]:
                tob_changed = True
                self.current_ask = self.list_asks[0]

        if tob_changed:
            be = self.create_book_event(self.current_bid, self.current_ask)
            if self.ob_to_ts is not None:
                self.ob_to_ts.append(be)
            else:
                return be
