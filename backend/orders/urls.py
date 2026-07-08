from django.urls import path

from .views import (
    PlaceOrderView,
    PaystackWebhookView,
    OrderDetailView,
    MyOrdersView,
    DeliveryZonesView,
)

urlpatterns = [
    path('delivery-zones/', DeliveryZonesView.as_view(), name='delivery-zones'),
    path('place/', PlaceOrderView.as_view(), name='place-order'),
    path('webhook/paystack/', PaystackWebhookView.as_view(), name='paystack-webhook'),
    path('mine/', MyOrdersView.as_view(), name='my-orders'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
]
