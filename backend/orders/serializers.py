from rest_framework import serializers

from store.models import Product, ProductSize, AddOn
from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    size_id = serializers.IntegerField(required=False, allow_null=True)
    add_on_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    size_name = serializers.CharField(source='size.name', read_only=True, default=None)
    add_ons = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'product_name', 'size', 'size_name',
            'add_ons', 'quantity', 'unit_price', 'line_total',
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'delivery_name', 'delivery_phone',
            'delivery_address', 'delivery_fee', 'subtotal', 'total',
            'paystack_reference', 'created_at', 'items',
        )
        read_only_fields = (
            'id', 'order_number', 'status', 'subtotal', 'total',
            'paystack_reference', 'created_at',
        )


DELIVERY_FEE = 1500


class CreateOrderSerializer(serializers.Serializer):
    delivery_name = serializers.CharField(max_length=150)
    delivery_phone = serializers.CharField(max_length=20)
    delivery_address = serializers.CharField(max_length=255)
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")
        return items

    def create(self, validated_data):
        request = self.context['request']
        items_data = validated_data.pop('items')

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            delivery_name=validated_data['delivery_name'],
            delivery_phone=validated_data['delivery_phone'],
            delivery_address=validated_data['delivery_address'],
            delivery_fee=DELIVERY_FEE,
        )

        subtotal = 0
        for item in items_data:
            product = Product.objects.get(pk=item['product_id'])
            size = None
            unit_price = product.base_price
            if item.get('size_id'):
                size = ProductSize.objects.get(pk=item['size_id'], product=product)
                unit_price = size.price

            add_ons = AddOn.objects.filter(pk__in=item.get('add_on_ids', []))
            add_on_total = sum(a.price for a in add_ons)
            unit_price_with_addons = unit_price + add_on_total
            line_total = unit_price_with_addons * item['quantity']
            subtotal += line_total

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                size=size,
                quantity=item['quantity'],
                unit_price=unit_price_with_addons,
                line_total=line_total,
            )
            order_item.add_ons.set(add_ons)

        order.subtotal = subtotal
        order.total = subtotal + order.delivery_fee
        order.save()
        return order
