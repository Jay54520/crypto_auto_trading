# -*- coding: utf-8 -*-

from strategy.models import Order
from strategy.utils import generate_orders


def create_orders(sender, instance, created, **kwargs):
    """根据策略创建订单"""
    strategy = instance
    # 禁用相同 symbol 的所有订单
    Order.objects.filter(strategy__symbol=strategy.symbol).update(is_valid=False)

    orders = generate_orders(strategy.symbol, strategy.side, strategy.quantity, strategy.start_dt,
                             strategy.end_dt, strategy)

    for order in orders:
        Order.objects.create(**order)
