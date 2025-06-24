import unittest
from api import server_simulator
from models.models import Fills

STOCK_POOL = ["stock_01", "stock_02", "stock_03", "stock_04", "stock_05",
              "stock_06", "stock_07", "stock_08", "stock_09", "stock_10"]
PRICE_MIN = 10
PRICE_MAX = 50
QUANTITY_MIN = 20
QUANTITY_MAX = 40


class TestServerSimulator(unittest.TestCase):

    def test_generate_fills(self):
        rtn = server_simulator.generate_fills()
        self.assertEqual(len(rtn.model_dump().items()), 3)
        self.assertEqual(check_generate_fills_range(rtn), True)


def check_generate_fills_range(a: Fills) -> bool:
    tag_st, tag_price, tag_qt = False, False, False
    if a.stock_ticker in STOCK_POOL:
        tag_st = True
    if a.price >= PRICE_MIN and a.price <= PRICE_MAX:
        tag_price = True
    if a.quantity >= QUANTITY_MIN and a.quantity <= QUANTITY_MAX:
        tag_qt = True
    return tag_st and tag_price and tag_qt
