from django.urls import path

from .views import (
    InitiateCheckoutView,
    PaystackWebhookView,
    OrderDetailView,
    MyOrdersView,
    DebugConfigView,
)

urlpatterns = [
    path('debug-config/', DebugConfigView.as_view(), name='debug-config'),
    path('initiate/', InitiateCheckoutView.as_view(), name='initiate-checkout'),
    path('webhook/paystack/', PaystackWebhookView.as_view(), name='paystack-webhook'),
    path('mine/', MyOrdersView.as_view(), name='my-orders'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
]
