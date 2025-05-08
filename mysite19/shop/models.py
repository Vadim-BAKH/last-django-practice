"""Модели приложения"""

from django.contrib.auth.models import User
from django.core.validators import (MaxLengthValidator, MaxValueValidator,
                                    MinValueValidator)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    """
    Путь для превью изображения продукта.
    """
    return f"products/product_{instance.pk}/preview/{filename}"


class Product(models.Model):
    """
    Модель товара интернет магазина
    с основными характеристиками.

    Ссылка на заказы: :model:`shop.Order`
    """

    class Meta:
        ordering = ["name"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(
        max_length=100,
        null=False,
        db_index=True
    )
    description = models.TextField(
        null=False,
        blank=True,
        validators=[MaxLengthValidator(300)],
        db_index=True
    )
    price = models.DecimalField(
        default=0,
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )
    discount = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MaxValueValidator(100),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(
        null=True, blank=True, upload_to=product_preview_directory_path
    )

    def get_absolute_url(self):
        return reverse("shop:product_details", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"Product(pk={self.pk},"\
               f" name={self.name!r},"\
               f" price={self.price})"


def product_images_directory_path(
        instance: "ProductImage", filename: str
) -> str:
    """
    Путь для изображений товара.
    """
    return f"products/product_{instance.product.pk}/images/{filename}"


class ProductImage(models.Model):
    """
    Модель изображения, связанного с товаром.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=product_images_directory_path)


class Order(models.Model):
    """
    Модель заказа с адресом, пользователем и товарами.

    Ссылка на продукты: :model:`shop.Product`
    """

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(null=False, db_index=True)
    promo_code = models.CharField(max_length=25, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")

    def __str__(self) -> str:
        return (
            f"Order(pk={self.pk},"
            f" delivery__address={self.delivery_address!r},"
            f" created_at={self.created_at})"
        )
