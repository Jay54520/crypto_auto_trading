# -*- coding: utf-8 -*-
from binance.client import Client
from django.conf import settings

from strategy.models import Symbol

client = Client(settings.API_KEY, settings.API_SECRET)


def update_symbol_info():
    """
    更新币安 symbol 信息到 Symbol model
    :return:
    """
    info = client.get_exchange_info()
    symbol_info_list = info['symbols']
    for symbol_info in symbol_info_list:
        min_qty = symbol_info['filters'][1]['minQty']
        step_size = symbol_info['filters'][1]['stepSize']
        Symbol.objects.update_or_create(
            defaults={
                'base_asset': symbol_info['baseAsset'],
                'quote_asset': symbol_info['quoteAsset'],
                'min_qty': min_qty,
                'step_size': step_size,
            },
            name=symbol_info['symbol']
        )
