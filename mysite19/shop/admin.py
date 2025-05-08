"""Административные классы и действия для моделей"""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from .admin_mixins import ExportAsCSVMixin
from .common import save_csv_orders, save_csv_products
from .forms import CSVImportForm
from .models import Order, Product, ProductImage


class ProductImageInLine(admin.StackedInline):
    """
    Inline для отображения изображений продукта в админке.
    """

    model = ProductImage


class OrderInline(admin.TabularInline):
    """
    Inline для отображения связей заказов с продуктами в табличном виде.
    """

    model = Product.orders.through


@admin.action(description="Archive products")
def mark_archived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
) -> None:
    """
    Админ-действие для пометки выбранных продуктов как архивированных.

    Args:
        modeladmin: Админ-модель.
        request: HTTP-запрос.
        queryset: Выбранные объекты для действия.
    """
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
) -> None:
    """
    Админ-действие для снятия пометки архивности с выбранных продуктов.

    Args:
        modeladmin: Админ-модель.
        request: HTTP-запрос.
        queryset: Выбранные объекты для действия.
    """
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(
    admin.ModelAdmin, ExportAsCSVMixin
):
    """
    Админ-класс для модели Product с настройками
    отображения, фильтрации и действий.
    """
    change_list_template = "shop/products_change_list.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductImageInLine,
    ]

    list_display = ("pk",
                    "name",
                    "description_short",
                    "price",
                    "discount",
                    "archived")
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (
            None,
            {
                "fields": ("name", "description"),
            },
        ),
        (
            "Price options",
            {
                "fields": ("price", "discount"),
                "classes": ("wide", "collapse"),
            },
        ),
        (
            "images",
            {
                "fields": ("preview",),
            },
        ),
        (
            "Extra options",
            {
                "fields": ("archived",),
                "classes": ("collapse",),
                "description":
                    "Extra options. Field 'archived' is for soft delete",
            },
        ),
    ]

    def description_short(self, obj: Product) -> str:
        """
        Возвращает укороченное описание продукта (до 48 символов).

        Args:
            obj: Экземпляр продукта.

        Returns:
            Краткое описание с многоточием, если длиннее 48 символов.
        """
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context=context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(
                request,
                "admin/csv_form.html",
                context=context,
                status=400
            )
        save_csv_products(
            file=form.cleaned_data["csv_file"],
            encoding=request.encoding,
            user=request.user,
        )
        self.message_user(request, "Data from CSV was imported.")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-product-csv/",
                 self.import_csv,
                 name="import_products_csv",
            )
        ]
        return new_urls + urls


class ProductInline(admin.StackedInline):
    """
    Inline для отображения связей продуктов с заказами в админке.
    """

    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Order с настройками
    отображения и оптимизацией запросов.
    """
    change_list_template = "shop/orders_change_list.html"
    inlines = [
        ProductInline,
    ]
    list_display = ("delivery_address",
                    "promo_code",
                    "created_at",
                    "user_verbose")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Оптимизированный queryset.

        Args:
            request: HTTP-запрос.

        Returns:
            Оптимизированный queryset заказов.
        """
        return (Order.objects
                .select_related("user")
                .prefetch_related("products"))

    def user_verbose(self, obj: Order) -> str:
        """
        Отображает имя пользователя или его username.

        Args:
            obj: Экземпляр заказа.

        Returns:
            Строка с именем пользователя.
        """
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context=context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(
                request,
                "admin/csv_form.html",
                context=context,
                status=400
            )
        save_csv_orders(
            file=form.cleaned_data["csv_file"],
            encoding=request.encoding,
            user=request.user,
        )
        self.message_user(request, "Data from CSV was imported.")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-order-csv/",
                 self.import_csv,
                 name="import_orders_csv",
            )
        ]
        return new_urls + urls
