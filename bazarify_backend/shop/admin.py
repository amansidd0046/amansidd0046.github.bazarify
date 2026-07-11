from django.contrib import admin

from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "category", "price", "stock"]
    list_filter = ["category", "stock"]
    search_fields = ["sku", "name"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "unit_price", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "user", "phone", "total", "payment_method", "created_at"]
    list_filter = ["payment_method"]
    search_fields = ["order_number", "phone"]
    inlines = [OrderItemInline]
