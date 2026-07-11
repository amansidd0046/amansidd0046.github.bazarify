from django.conf import settings
from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("clothing", "Clothing"),
        ("shoes", "Shoes"),
        ("grocery", "Grocery"),
        ("electronics", "Electronics"),
        ("home", "Home"),
        ("beauty", "Beauty"),
    ]
    STOCK_CHOICES = [
        ("in", "In Stock"),
        ("low", "Low Stock"),
        ("sold", "Sold Out"),
    ]

    # Human-friendly SKU, matches the ids already used by the frontend
    # (p01, p02, ...) so the existing markup/icon lookup keeps working.
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.CharField(max_length=10, choices=STOCK_CHOICES, default="in")
    icon = models.CharField(max_length=30, help_text="Key into the frontend ICONS map")

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.sku} — {self.name}"

    @property
    def in_stock(self):
        return self.stock != "sold"


class Order(models.Model):
    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("upi", "UPI"),
        ("card", "Card"),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
        help_text="Set if the shopper was logged in at checkout; guest checkout leaves this blank.",
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=12)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    # Snapshot the name/price at time of purchase so later catalog edits
    # don't rewrite historical orders.
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def line_total(self):
        return self.unit_price * self.quantity
