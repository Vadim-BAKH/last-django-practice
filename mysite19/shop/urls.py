"""
URL-конфигурация приложения shop.

Определяет маршруты для веб-страниц и API, включая

CRUD операции для продуктов и заказов.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (GroupsList, LatestProductsFeed, OrderCreateView,
                    OrderDeleteView, OrderDetailView, OrdersListView,
                    OrdersOwnerDataExportView, OrderUpdateView, OrderViewSet,
                    ProductCreateView, ProductDeleteView, ProductDetailsView,
                    ProductsDataExportView, ProductsListView,
                    ProductUpdateView, ProductViewSet, ShopIndex,
                    UserOrderListView)

app_name = "shop"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    path("", ShopIndex.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupsList.as_view(), name="groups"),
    path("products/", ProductsListView.as_view(), name="products"),
    path(
        "products/export/",
        ProductsDataExportView.as_view(),
        name="products-export"
    ),
    path(
        "products/<int:pk>/",
        ProductDetailsView.as_view(),
        name="product_details"
    ),
    path(
        "products/<int:pk>/update",
        ProductUpdateView.as_view(),
        name="product_update"
    ),
    path(
        "products/latest/feed/",
        LatestProductsFeed(),
        name="products_feed"
    ),
    path("orders/", OrdersListView.as_view(), name="orders"),
    path(
        "users/<int:user_id>/orders/",
        UserOrderListView.as_view(),
        name="user_orders"
    ),
    path(
        "users/<int:user_id>/orders/export/",
        OrdersOwnerDataExportView.as_view(),
        name="owner_orders_export",
    ),
    path(
        "products/create/",
        ProductCreateView.as_view(),
        name="create_product"
    ),
    path(
        "products/<int:pk>/archive",
        ProductDeleteView.as_view(),
        name="product_archive"
    ),
    path("orders/create/", OrderCreateView.as_view(), name="create_order"),
    path("orders/<int:pk>", OrderDetailView.as_view(), name="order_details"),
    path(
        "orders/<int:pk>/update",
        OrderUpdateView.as_view(),
        name="order_update"
    ),
    path(
        "orders/<int:pk>/delete",
        OrderDeleteView.as_view(),
        name="order_delete"
    ),
]
