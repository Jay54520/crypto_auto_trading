# -*- coding: utf-8 -*-
import time

import datetime
import decimal
import typing
from binance.client import Client
from django.conf import settings

from crypto_auto_trading import constants
from strategy.models import Symbol, Strategy, Order

client = Client(settings.API_KEY, settings.API_SECRET)


def update_symbol_info():
    """
    更新币安 symbol 信息到 Symbol model
    :return:
    """
    info = client.get_exchange_info()
    symbol_info_list = info['symbols']
    for symbol_info in symbol_info_list:
        min_price = symbol_info['filters'][0]['minPrice']
        min_qty = symbol_info['filters'][1]['minQty']
        step_size = symbol_info['filters'][1]['stepSize']
        min_notional = symbol_info['filters'][2]['minNotional']
        Symbol.objects.update_or_create(
            defaults={
                'base_asset': symbol_info['baseAsset'],
                'quote_asset': symbol_info['quoteAsset'],
                'min_qty': min_qty,
                'min_price': min_price,
                'min_notional': min_notional,
                'step_size': step_size,
            },
            name=symbol_info['symbol']
        )


def get_model_field_names(model, is_relation=False):
    field_names = []
    for field in model._meta.get_fields():
        if field.is_relation == is_relation:
            field_names.append(field.name)
    return field_names


def get_price(symbol, side) -> decimal.Decimal:
    """获取价格
    目前的策略是买入价格为最高买价，卖出价格为最低卖价。相对于买入价格为最低卖价，成交率一定会较低，如果能成交，成本会减小
    """
    price_info = client.get_orderbook_ticker(symbol=symbol)
    if side == constants.BUY:
        price = price_info['bidPrice']
    else:
        price = price_info['askPrice']
    return decimal.Decimal(price)


def generate_dts(start_dt: datetime.datetime, end_dt: datetime.datetime, delta: datetime.timedelta) -> typing.List[
    datetime.datetime]:
    """生成从开始时间大于等于 start_dt，结束时间小于等于 end_dt，间隔为 delta 的时间列表"""
    dt = start_dt
    dts = []
    while dt <= end_dt:
        dts.append(dt)
        dt += delta
    return dts


def round_to_template(num: decimal.Decimal, example: decimal.Decimal) -> decimal.Decimal:
    """
    将 num 四舍五入到 example 所在的位数
    :param num:
    :param example: 必须含有 1，比如 decimal.Decimal('0.01')、decimal.Decimal('0.000001000')
    :return:
    """
    example = str(example)
    if '1' not in example:
        raise ValueError('example 必须包含 1')
    return round(num, example.index('1') - 1)


def format_quantity(quantity, step_size):
    """根据 step_size 格式化 quantity，使满足 (quantity-minQty) % stepSize == 0"""
    # + symbol.step_size 的原因是防止四舍五入后变小了
    return round_to_template(quantity, step_size) + step_size


def get_min_quantity(symbol: Symbol, side, price=None) -> decimal.Decimal:
    """获取能够交易的最低数量"""
    order_price = price or get_price(symbol.name, side)
    min_quantity = symbol.min_notional / order_price
    min_quantity = format_quantity(min_quantity, symbol.step_size)
    return min_quantity


def generate_orders(symbol: Symbol, side, quantity, start_dt, end_dt, strategy: Strategy = None):
    """返回创建  order 的必须数据，order 分布到 start_dt, end_dt 中
    strategy 参数不参与逻辑，只是用作创建  order
    """
    orders = []
    min_quantity = get_min_quantity(symbol, side)
    if min_quantity > quantity:
        raise ValueError('最小数量 {} 大于策略数量 {}'.format(min_quantity, quantity))

    max_order_times = int(quantity // min_quantity)
    remaining_quantity = quantity - min_quantity * max_order_times
    order_time_delta = (end_dt - start_dt) / max_order_times
    dts = generate_dts(start_dt, end_dt, order_time_delta)
    for dt in dts:
        if dt == end_dt:
            # 将剩余数量加到最后一次交易中。不加到前面的原因是前面可能低于最小限制，因此可作为补充
            order_quantity = min_quantity + remaining_quantity
        else:
            order_quantity = min_quantity
        order = {
            'time': dt,
            'quantity': order_quantity,
            'is_valid': True
        }
        if strategy:
            order['strategy'] = strategy
        orders.append(order)
        dt += order_time_delta
    return orders


def place_test_order(order: Order):
    """下单"""
    strategy = order.strategy
    price = get_price(strategy.symbol.name, strategy.side)
    min_quantity = get_min_quantity(strategy.symbol, strategy.side, price)
    quantity = order.quantity
    # 因为订单是预估的，所以实际下单时可能会低于最小数量
    if quantity < min_quantity:
        quantity = min_quantity
        order.quantity = quantity
        order.save()

    result = client.create_test_order(
        symbol=strategy.symbol.name,
        side=strategy.side,
        type=constants.TYPE_LIMIT,
        timeInForce=constants.GTC,
        quantity=order.quantity,
        price=price,
        timestamp=int(time.time())
    )
    return result