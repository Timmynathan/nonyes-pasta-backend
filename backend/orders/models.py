import uuid

from django.conf import settings
from django.db import models

from store.models import Product, ProductSize, AddOn


class PendingOrder(models.Model):
    """Holds cart + customer details until Paystack webhook confirms payment."""
    reference = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    delivery_name = models.CharField(max_length=150)
    delivery_phone = models.CharField(max_length=20)
    delivery_address = models.CharField(max_length=255)
    cart = models.JSONField()  # list of {product_id, size_id, add_on_ids, quantity, spice_level}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PendingOrder {self.reference}"


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_PREPARING = 'preparing'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_OUT_FOR_DELIVERY, 'Out for Delivery'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    delivery_name = models.CharField(max_length=150)
    delivery_phone = models.CharField(max_length=20)
    delivery_address = models.CharField(max_length=255, help_text="Delivery address within Lagos")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    paystack_reference = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"NP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    SPICE_MILD = 'mild'
    SPICE_EXTRA = 'extra'
    SPICE_CHOICES = [
        (SPICE_MILD, 'Mild Spicy'),
        (SPICE_EXTRA, 'Extra Spicy'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
    add_ons = models.ManyToManyField(AddOn, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    spice_level = models.CharField(max_length=10, choices=SPICE_CHOICES, default=SPICE_MILD, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted product'}"
