from django.contrib import admin

from strategy.models import Strategy, Order, Symbol
from strategy.utils import get_model_field_names


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = get_model_field_names(Symbol)
    list_filter = ('base_asset', 'quote_asset')
    search_fields = ('name', 'base_asset', 'quote_asset')
    ordering = ('name', 'base_asset', 'quote_asset')


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = get_model_field_names(Strategy)
    list_filter = ('side',)
    search_fields = ('symbol',)
    ordering = ('symbol', 'start_dt')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = get_model_field_names(Order)
    list_filter = ('strategy', 'is_valid', 'status')
    search_fields = ('strategy',)
    ordering = ('time', 'strategy')
