from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product, AddOn, Review
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    AddOnSerializer, ReviewSerializer, NewsletterSubscriberSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('sizes', 'reviews')
    lookup_field = 'slug'
    search_fields = ('name', 'description')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer


class AddOnViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AddOn.objects.filter(is_active=True)
    serializer_class = AddOnSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        product_slug = self.request.query_params.get('product')
        if product_slug:
            qs = qs.filter(product__slug=product_slug)
        return qs


class NewsletterSubscribeView(generics.CreateAPIView):
    serializer_class = NewsletterSubscriberSerializer
    permission_classes = [permissions.AllowAny]
