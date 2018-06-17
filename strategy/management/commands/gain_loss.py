# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from strategy.models import Symbol
from strategy.utils import gain_loss


class Command(BaseCommand):
    help = '持仓盈亏'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str)

    def handle(self, *args, **options):
        symbol = options['symbol']
        symbol = Symbol.objects.get(name=symbol)
        cost_usdt, holding_asset_to_usdt, percentage = gain_loss(symbol)
        self.stdout.write('cost_usdt: {}, holding_asset_to_usdt: {}, percentage: {}'.format(
            cost_usdt, holding_asset_to_usdt, percentage
        ))
