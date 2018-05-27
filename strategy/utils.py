# -*- coding: utf-8 -*-
import time

import datetime
import decimal
import typing
from huobi import HuobiRestClient
from django.conf import settings

from crypto_auto_trading import constants
from strategy.models import Symbol, Strategy, Order

client = HuobiRestClient(settings.API_KEY, settings.API_SECRET)


def get_spot_account_id() -> int:
    accounts = client.accounts().data['data']
    for account in accounts:
        if not account['type'] == 'spot':
            continue
        return account['id']
    raise Exception('没有找到 spot account id')


client.account_id = get_spot_account_id()


def get_min_qty(symbol: str) -> decimal.Decimal:
    """获取火币中 symbol 对应的最小交易数量。目前人工处理。
    API 中没有提供，可从 https://huobiglobal.zendesk.com/hc/zh-cn/articles/360000076392-%E4%BA%A4%E6%98%93%E9%99%90%E9%A2%9D
    获取
    由于交易对添加的很慢，所以手动处理就行
    """
    min_qty_dict = {
        'btcusdt': decimal.Decimal('0.001'),
        'bchusdt': decimal.Decimal('0.001'),
        'cvcusdt': decimal.Decimal('0.1'),
        'dtausdt': decimal.Decimal('1'),
        'dashusdt': decimal.Decimal('0.001'),
        'ethusdt': decimal.Decimal('0.001'),
        'etcusdt': decimal.Decimal('0.01'),
        'eosusdt': decimal.Decimal('0.01'),
        'elfusdt': decimal.Decimal('0.1'),
        'elausdt': decimal.Decimal('0.001'),
        'gntusdt': decimal.Decimal('0.1'),
        'htusdt': decimal.Decimal('0.1'),
        'hsrusdt': decimal.Decimal('0.01'),
        'itcusdt': decimal.Decimal('0.01'),
        'iostusdt': decimal.Decimal('1'),
        'letusdt': decimal.Decimal('1'),
        'ltcusdt': decimal.Decimal('0.001'),
        'mdsusdt': decimal.Decimal('0.1'),
        'neousdt': decimal.Decimal('0.001'),
        'nasusdt': decimal.Decimal('0.01'),
        'omgusdt': decimal.Decimal('0.01'),
        'qtumusdt': decimal.Decimal('0.01'),
        'ruffusdt': decimal.Decimal('1'),
        'sntusdt': decimal.Decimal('0.1'),
        'storjusdt': decimal.Decimal('0.01'),
        'smtusdt': decimal.Decimal('1'),
        'trxusdt': decimal.Decimal('1'),
        'thetausdt': decimal.Decimal('0.1'),
        'venusdt': decimal.Decimal('0.1'),
        'xrpusdt': decimal.Decimal('1'),
        'xemusdt': decimal.Decimal('0.1'),
        'zecusdt': decimal.Decimal('0.001'),
        'zilusdt': decimal.Decimal('1'),
    }
    return min_qty_dict[symbol]


def get_num_from_precision(precision: int) -> decimal.Decimal:
    if precision < 0:
        raise ValueError('precision 不能小于 0')
    return decimal.Decimal('1e{}'.format(-precision))


def update_symbol_info():
    """
    更新火币 symbol 信息到 Symbol model
    :return:
    """
    info = client.symbols().data
    symbol_info_list = info['data']
    for symbol_info in symbol_info_list:
        name = symbol_info['base-currency'] + symbol_info['quote-currency']
        try:
            min_qty = get_min_qty(name)
        except KeyError:
            continue
        min_price = get_num_from_precision(precision=symbol_info['price-precision'])
        step_size = get_num_from_precision(precision=symbol_info['amount-precision'])
        min_notional = min_price * min_qty

        Symbol.objects.update_or_create(
            defaults={
                'base_asset': symbol_info['base-currency'],
                'quote_asset': symbol_info['quote-currency'],
                'min_qty': min_qty,
                'min_price': min_price,
                'min_notional': min_notional,
                'step_size': step_size,
            },
            name=name
        )


def get_model_field_names(model, is_relation=False):
    field_names = []
    for field in model._meta.get_fields():
        if field.is_relation == is_relation:
            field_names.append(field.name)
    return field_names


def get_price(symbol: Symbol, side) -> decimal.Decimal:
    """获取价格
    目前的策略是买入价格为最高买价，卖出价格为最低卖价。相对于买入价格为最低卖价，成交率一定会较低，如果能成交，成本会减小
    """
    price_info = client.market_depth(symbol=symbol.name).data
    if side == constants.BUY:
        price = decimal.Decimal(price_info['tick']['bids'][0][0])
    else:
        price = decimal.Decimal(price_info['tick']['asks'][0][0])
    return round_to_template(price, symbol.min_price)


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
    index = example.index('1')
    if index == 0:
        ndigits = 0
    else:
        # 减一的原因是存在小数点
        ndigits = index - 1
    return round(num, ndigits)


def format_quantity(quantity, step_size):
    """根据 step_size 格式化 quantity，使满足 (quantity-minQty) % stepSize == 0"""
    # + symbol.step_size 的原因是防止四舍五入后变小了
    return round_to_template(quantity, step_size) + step_size


def get_min_quantity(symbol: Symbol) -> decimal.Decimal:
    """获取能够交易的最低数量"""
    return round_to_template(symbol.min_qty, symbol.min_qty)


def generate_orders(symbol: Symbol, quantity, start_dt, end_dt, strategy: Strategy = None):
    """返回创建  order 的必须数据，order 分布到 start_dt, end_dt 中
    strategy 参数不参与逻辑，只是用作创建  order
    """
    orders = []
    min_quantity = get_min_quantity(symbol)
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
        order_quantity = round_to_template(order_quantity, symbol.min_qty)
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


def place_order(order: Order):
    """下单"""
    strategy = order.strategy
    price = get_price(strategy.symbol, strategy.side)
    min_quantity = get_min_quantity(strategy.symbol)
    quantity = order.quantity
    # 因为订单是预估的，所以实际下单时可能会低于最小数量
    if quantity < min_quantity:
        quantity = min_quantity
        order.quantity = quantity
        order.save()
    quantity = str(round_to_template(order.quantity, strategy.symbol.min_qty)),
    price = str(price)
    result = client.place(
        account_id=client.account_id,
        amount=quantity,
        price=price,
        source='api',
        symbol=strategy.symbol.name,
        type=strategy.side
    ).data
    if result['status'] == 'ok':
        order.quantity=quantity
        order.price=price
        order.status = 'submitted'
        order.order_id = result['data']
        order.save()
    else:
        print('order_id: {}, result: {}'.format(order.id, result))

