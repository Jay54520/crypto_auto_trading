# -*- coding: utf-8 -*-
import datetime

from django.core.management.base import BaseCommand

from strategy.models import Order
from strategy.utils import update_symbol_info, place_test_order


class Command(BaseCommand):
    help = '下当前分钟内的订单'

    def handle(self, *args, **options):
        current_minute = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        next_minute = current_minute + datetime.timedelta(minutes=1)
        orders = Order.objects.filter(
            time__gte=current_minute,
            time__lt=next_minute
        )
        for order in orders:
            place_test_order(order)
        self.stdout.write('下单 {} 笔'.format(orders.count()))
