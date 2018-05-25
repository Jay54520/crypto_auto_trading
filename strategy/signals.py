# -*- coding: utf-8 -*-

from strategy.models import Order
from strategy.utils import generate_orders


def create_orders(sender, instance, created, **kwargs):
    """根据策略创建订单"""
    strategy = instance
    if not created:
        # 修改策略后删除旧策略对应的订单，然后在下面重新生成
        Order.objects.filter(strategy=strategy).delete()

    orders = generate_orders(strategy.symbol, strategy.side, strategy.quantity, strategy.start_dt,
                             strategy.end_dt, strategy)

    for order in orders:
        Order.objects.create(**order)
