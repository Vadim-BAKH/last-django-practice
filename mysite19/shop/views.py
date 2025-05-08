"""Представления моделей интернет магазина"""

# import logging
from csv import DictWriter
from typing import Any, Optional

from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from loguru import logger
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .common import save_csv_products
from .forms import GroupForm, OrderForm, ProductForm
from .models import Order, Product, ProductImage
from .serializers import OrderSerializer, ProductSerializer

# log = logging.getLogger(__name__)

class OrdersOwnerDataExportView(View):
    """
    Представление для экспорта заказов.

    Заказы конкретного пользователя в JSON формате.
    """
    def setup(self, request, *args, **kwargs):
        """
        Инициализация экземпляра представления.

        Получает user_id из параметров URL.
        Загружает пользователя.
        """
        super().setup(request, *args, **kwargs)
        user_id = self.kwargs["user_id"]
        self.owner = get_object_or_404(User, id=user_id)

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """
        Обрабатывает GET-запрос.

        Возвращает JSON с данными заказов пользователя.
        Кэширует результат на 300 секунд.
        """
        cache_key = f"orders_owner_export_{self.owner.id}"
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = (
                Order.objects
                      .filter(user=self.owner)
                      .select_related("user")
                      .prefetch_related("products")
                      .order_by('-pk').all()
            )

            orders_data = [
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "promo_code": order.promo_code,
                    "created_at": order.created_at.isoformat(),
                    "products": [
                        {
                            "pk": product.pk,
                            "name": product.name,
                            "price": product.price,
                            "discount": product.discount,
                        }
                        for product in order.products.all()
                    ],
                }
                for order in orders
            ]
        cache.set(cache_key, orders_data, 300)
        return JsonResponse({"orders": orders_data})


class UserOrderListView(LoginRequiredMixin, ListView):
    """Список заказов конкретного пользователя."""
    model = Order
    template_name = "shop/user_orders.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        user_id = self.kwargs["user_id"]
        self.owner = get_object_or_404(User, id=user_id)

    def get_queryset(self):
        return (Order.objects
                .filter(user=self.owner)
                .select_related("user")
                .prefetch_related("products"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "owner": self.owner,
            "order_verbose_name": Order._meta.verbose_name,
            "orders_verbose_name": Order._meta.verbose_name_plural,
        })
        logger.debug(f"Открыты заказы {self.owner.username}")
        return context


class LatestProductsFeed(Feed):
    title = "The latest receipts of goods"
    description = "The latest and most delicious products"
    link = reverse_lazy("shop:products")

    def items(self):
        return Product.objects.filter(archived=False).order_by("-created_at")[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:100]

    def item_pubdate(self, item: Product):
        return item.created_at



@extend_schema(description="Order views CRUD")
class OrderViewSet(ModelViewSet):
    """
    ViewSet REST Framework для управления заказами.

    Полный CRUD для сущности заказа.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        "delivery_address",
    ]
    filterset_fields = [
        "delivery_address",
        "user",
        "products",
    ]
    ordering_fields = [
        "created_at",
    ]


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    ViewSet REST Framework для управления товарами.

    Полный CRUD для сущности товара.
    """
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "created_by",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(
                description="Empty response, product by id not found"
            ),
        }
    )
    @method_decorator(cache_page(30))
    def retrieve(self, *args, **kwargs):
        logger.debug("Привет получение продукта")
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(30))
    def list(self, *args, **kwargs):
        logger.debug("Привет список продуктов")
        return super().list(*args, **kwargs)


    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products_export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
            "created_by",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "No file uploaded."}, status=400)
        products = save_csv_products(
            file.file,
            encoding=request.encoding or "utf-8",
            user=request.user,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ProductCreateView(UserPassesTestMixin, CreateView):
    """
    Создание товара с проверкой прав и

    загрузкой изображений.
    """

    def test_func(self) -> bool:
        """
        Проверка разрешения на добавление продукта.
        """
        return self.request.user.has_perm("shop.add_product")

    def form_valid(self, form: Any) -> HttpResponse:
        """
        Обработка валидной формы и сохранение изображений.
        """
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        for image in form.files.getlist("images"):
            ProductImage.objects.create(product=self.object, image=image)
        return response

    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shop:products")


class ProductDetailsView(DetailView):
    """Детальный просмотр товара."""

    template_name = "shop/product-details.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    """
    Обновление товара с проверкой прав

    и загрузкой изображений.
    """

    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def form_valid(self, form: Any) -> HttpResponse:
        """
        Обработка валидной формы и сохранение новых изображений.
        """
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(product=self.object, image=image)
        return response

    def get_success_url(self) -> str:
        """
        URL для перенаправления после успешного обновления.
        """
        return reverse(
            "shop:product_details",
            kwargs={"pk": self.object.pk},
        )

    def test_func(self) -> bool:
        """
        Проверка разрешения на изменение продукта.
        """
        if self.request.user.is_superuser:
            return True
        return (
            self.request.user.has_perm("shop.change_product")
            and self.get_object().created_by == self.request.user
        )


class ProductDeleteView(DeleteView):
    """Архивирование товара вместо удаления."""

    model = Product
    success_url = reverse_lazy("shop:products")

    def form_valid(self, form: Any) -> HttpResponseRedirect:
        """Пометка продукта как архивированного."""
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductsListView(ListView):
    """Список активных товаров."""

    model = Product
    template_name = "shop/products-list.html"
    context_object_name = "products"

    def get_queryset(self) -> Any:
        """Получить только неархивированные продукты."""
        return Product.objects.filter(archived=False)

    def get_context_data(self, **kwargs: Any) -> dict:
        """
        Добавить в контекст имена модели во

        множественном и единственном числе.
        """
        context = super().get_context_data(**kwargs)
        context["product_verbose_name"] = Product._meta.verbose_name
        context["products_verbose_name"] = Product._meta.verbose_name_plural
        logger.debug("Открыт список продуктов")
        return context


class OrderCreateView(UserPassesTestMixin, CreateView):
    """Создание заказа с проверкой прав."""

    def test_func(self) -> bool:
        """Проверка разрешения на добавление заказа."""
        return self.request.user.has_perm("shop.add_order")

    def form_valid(self, form: Any) -> HttpResponse:
        """Сохранение заказа и связанных продуктов."""
        order = form.save(commit=False)
        order.save()
        products = form.cleaned_data["products"]
        order.products.set(products)
        return super().form_valid(form)

    form_class = OrderForm
    success_url = reverse_lazy("shop:orders")
    template_name = "shop/order_form.html"


class OrdersListView(LoginRequiredMixin, ListView):
    """Список заказов с оптимизацией запросов."""

    queryset = (Order.objects.select_related("user")
                .prefetch_related("products"))

    def get_context_data(self, **kwargs: Any) -> dict:
        """
        Добавить в контекст имена модели во

        множественном и единственном числе.
        """
        context = super().get_context_data(**kwargs)
        context["order_verbose_name"] = Order._meta.verbose_name
        context["orders_verbose_name"] = Order._meta.verbose_name_plural
        logger.debug("Открыт список заказов")
        return context


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """Детальный просмотр заказа с проверкой прав."""
    permission_required = "shop.view_order"
    queryset = (Order.objects.select_related("user")
                .prefetch_related("products"))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        logger.debug(f"Посмотрели детали заказа: {obj.pk}")
        return obj



class OrderUpdateView(UpdateView):
    """
    Обновление заказа с поддержкой

    связанных продуктов.
    """

    queryset = (Order.objects.select_related("user")
                .prefetch_related("products"))
    template_name_suffix = "_update_form"
    form_class = OrderForm

    def form_valid(self, form: Any) -> HttpResponse:
        """
        Сохранение изменений заказа и связанных продуктов.
        """
        self.object = form.save(commit=False)
        self.object.save()
        products = form.cleaned_data["products"]
        self.object.products.set(products)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        URL для перенаправления после успешного обновления.
        """
        logger.info("Обновили заказ")
        return reverse("shop:order_details", kwargs={"pk": self.object.pk})


class OrderDeleteView(DeleteView):
    """Удаление заказа."""

    model = Order
    success_url = reverse_lazy("shop:orders")


class ShopIndex(View):
    """
    Главная страница магазина с основными ссылками.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработка GET-запроса, возвращает главную страницу.
        """
        context = {
            "hrefs": [
                "http://127.0.0.1:8000/shop/groups/",
                "http://127.0.0.1:8000/shop/products/",
                "http://127.0.0.1:8000/shop/orders/",
            ],
        }

        logger.debug(f"ShopIndexContext: {context}")
        return render(request, "shop/shop-index.html", context=context)


class GroupsList(View):
    """
    Страница со списком групп и формой создания новой группы.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработка GET-запроса, отображает список групп и форму.
        """
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shop/groups-list.html", context=context)

    def post(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Обработка POST-запроса, создаёт

        новую группу при валидной форме.
        """
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.path)


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products = Product.objects.order_by('pk').all()
        products_data = cache.get(cache_key)
        if products_data is None:
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "created_at": product.created_at,
                    "archived": product.archived,
                }
                for product in products
            ]
        cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})
