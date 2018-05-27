# -*- coding: utf-8 -*-
import datetime
import decimal
from django.test import TestCase
from unittest import mock

from crypto_auto_trading import constants
from strategy.models import Symbol
from strategy.utils import generate_orders, get_min_quantity


class TestGenerateOrders(TestCase):

    def setUp(self):
        self.symbol = Symbol.objects.create(
            name='XRPUSDT',
            min_qty=0.01,
            step_size=0.01,
            base_asset='XRP',
            quote_asset='USDT',
            min_notional=10,
            min_price=0.00001000
        )

    @mock.patch('strategy.utils.get_price', return_value=decimal.Decimal(0.62))
    def test_not_enough_qty(self, get_price):
        with self.assertRaises(ValueError):
            generate_orders(self.symbol, self.symbol.min_qty / 10, datetime.datetime(2018, 1, 1, 1),
                            datetime.datetime(2018, 1, 1, 2))

    @mock.patch('strategy.utils.get_price', return_value=decimal.Decimal(0.62))
    def test_success(self, get_price):
        orders = generate_orders(self.symbol,
                                 get_min_quantity(self.symbol) * 10,
                                 datetime.datetime(2018, 1, 1, 1),
                                 datetime.datetime(2018, 1, 1, 2))
        self.assertEqual([{'time': datetime.datetime(2018, 1, 1, 1, 0), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 6), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 12), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 18), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 24), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 30), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 36), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 42), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 48), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 1, 54), 'quantity': 0.01, 'is_valid': True},
                          {'time': datetime.datetime(2018, 1, 1, 2, 0), 'quantity': 0.01, 'is_valid': True}],
                         orders
                         )
