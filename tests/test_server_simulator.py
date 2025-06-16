import unittest
from api import server_simulator, STOCK_POOL, PRICE_MAX, PRICE_MIN, QUANTITY_MIN, QUANTITY_MAX


class TestServerSimulator(unittest.TestCase):

    def test_generate_fills(self):
        rtn = server_simulator.generate_fills()
        self.assertEqual(len(rtn.items()), 3)
        self.assertEqual(check_generate_fills_range(rtn), True)


def check_generate_fills_range(a: dict):
    tag_st, tag_price, tag_qt = False, False, False
    if a["stock_ticker"] in STOCK_POOL:
        tag_st = True
    if a["price"] >= PRICE_MIN and a["price"] <= PRICE_MAX:
        tag_price = True
    if a["quantity"] >= QUANTITY_MIN and a["quantity"] <= QUANTITY_MAX:
        tag_qt = True
    return tag_st and tag_price and tag_qt
