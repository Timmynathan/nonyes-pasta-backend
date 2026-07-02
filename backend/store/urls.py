from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, ProductViewSet, AddOnViewSet, ReviewViewSet,
    NewsletterSubscribeView,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('addons', AddOnViewSet, basename='addon')
router.register('reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('newsletter/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('', include(router.urls)),
]
