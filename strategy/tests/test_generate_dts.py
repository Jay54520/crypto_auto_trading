# -*- coding: utf-8 -*-
import datetime
from django.test import TestCase

from strategy.utils import generate_dts


class TestGenerateDts(TestCase):

    def test_normal_case(self):
        """测试正常情况：开始小于结束，delta 小于两者之间的差值"""
        dts = generate_dts(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 1, 2), datetime.timedelta(hours=1))
        self.assertEqual([datetime.datetime(2018, 1, 1, 0, 0), datetime.datetime(2018, 1, 1, 1, 0),
                          datetime.datetime(2018, 1, 1, 2, 0), datetime.datetime(2018, 1, 1, 3, 0),
                          datetime.datetime(2018, 1, 1, 4, 0), datetime.datetime(2018, 1, 1, 5, 0),
                          datetime.datetime(2018, 1, 1, 6, 0), datetime.datetime(2018, 1, 1, 7, 0),
                          datetime.datetime(2018, 1, 1, 8, 0), datetime.datetime(2018, 1, 1, 9, 0),
                          datetime.datetime(2018, 1, 1, 10, 0), datetime.datetime(2018, 1, 1, 11, 0),
                          datetime.datetime(2018, 1, 1, 12, 0), datetime.datetime(2018, 1, 1, 13, 0),
                          datetime.datetime(2018, 1, 1, 14, 0), datetime.datetime(2018, 1, 1, 15, 0),
                          datetime.datetime(2018, 1, 1, 16, 0), datetime.datetime(2018, 1, 1, 17, 0),
                          datetime.datetime(2018, 1, 1, 18, 0), datetime.datetime(2018, 1, 1, 19, 0),
                          datetime.datetime(2018, 1, 1, 20, 0), datetime.datetime(2018, 1, 1, 21, 0),
                          datetime.datetime(2018, 1, 1, 22, 0), datetime.datetime(2018, 1, 1, 23, 0),
                          datetime.datetime(2018, 1, 2, 0, 0)],
                         dts)

        dts = generate_dts(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 1, 1, 3),
                           datetime.timedelta(minutes=11))
        self.assertEqual([datetime.datetime(2018, 1, 1, 0, 0), datetime.datetime(2018, 1, 1, 0, 11),
                          datetime.datetime(2018, 1, 1, 0, 22), datetime.datetime(2018, 1, 1, 0, 33),
                          datetime.datetime(2018, 1, 1, 0, 44), datetime.datetime(2018, 1, 1, 0, 55),
                          datetime.datetime(2018, 1, 1, 1, 6), datetime.datetime(2018, 1, 1, 1, 17),
                          datetime.datetime(2018, 1, 1, 1, 28), datetime.datetime(2018, 1, 1, 1, 39),
                          datetime.datetime(2018, 1, 1, 1, 50), datetime.datetime(2018, 1, 1, 2, 1),
                          datetime.datetime(2018, 1, 1, 2, 12), datetime.datetime(2018, 1, 1, 2, 23),
                          datetime.datetime(2018, 1, 1, 2, 34), datetime.datetime(2018, 1, 1, 2, 45),
                          datetime.datetime(2018, 1, 1, 2, 56)],
                         dts)

    def test_start_greater_than_end(self):
        dts = generate_dts(datetime.datetime(2018, 1, 1), datetime.datetime(2017, 1, 2),
                           datetime.timedelta(hours=1))
        self.assertEqual([], dts)
