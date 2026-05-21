from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'transaction_type',
        'quantity',
        'unit_price',
        'total_price',
        'date',
        'user',
    )
    list_filter = ('transaction_type', 'date', 'user')
    search_fields = ('product__name', 'user__username')
