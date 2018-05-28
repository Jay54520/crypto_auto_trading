# -*- coding: utf-8 -*-
"""测试一些简单的 utils"""
import decimal
from django.test import TestCase

from strategy.utils import round_to_template


class TestUtils(TestCase):

    def test_round_to_template_exception(self):
        with self.assertRaises(ValueError):
            round_to_template(decimal.Decimal('0.1111'), decimal.Decimal('0.003'))

    def test_round_to_template(self):
        result = round_to_template(decimal.Decimal('16.589000000'), decimal.Decimal('0.01'))
        self.assertEqual(decimal.Decimal('16.59'), result)

        result = round_to_template(decimal.Decimal('16.584000000'), decimal.Decimal('0.01'))
        self.assertEqual(decimal.Decimal('16.58'), result)

        result = round_to_template(decimal.Decimal('16.584000000'), decimal.Decimal('1'))
        self.assertEqual(decimal.Decimal('17'), result)
