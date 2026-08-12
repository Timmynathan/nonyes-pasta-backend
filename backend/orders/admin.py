from django.contrib import admin

from .models import Order, OrderItem, DeliveryLocation


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'delivery_name', 'delivery_area', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'delivery_name', 'delivery_phone')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'paystack_reference')


@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'fee', 'arrange_privately', 'is_active')
    list_editable = ('fee', 'arrange_privately', 'is_active')   # edit right in the list
    list_filter = ('group', 'arrange_privately', 'is_active')
    search_fields = ('name', 'group')
    list_per_page = 100
