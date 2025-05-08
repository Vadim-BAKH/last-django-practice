"""Формы действий с моделями"""

from typing import Any, List, Optional, Union

from django.contrib.auth.models import Group
from django.forms import (CheckboxSelectMultiple, ClearableFileInput,
                          FileField, Form, ImageField, ModelForm,
                          ModelMultipleChoiceField)

from .models import Order, Product


class CSVImportForm(Form):
    csv_file = FileField()

class MultipleFileInput(ClearableFileInput):
    """
    Виджет для загрузки нескольких файлов.
    """

    allow_multiple_selected = True


class MultipleImageField(ImageField):
    """
    Поле для загрузки нескольких изображений одновременно.
    """

    widget = MultipleFileInput

    def clean(
        self, data: Union[List[Any], Any], initial: Optional[Any] = None
    ) -> Union[List[Any], Any]:
        """
        Очищает и валидирует данные поля.

        Если получен список или кортеж файлов, валидирует каждый файл отдельно.

        Args:
            data: Загруженные файлы (один или несколько).
            initial: Исходные данные (если есть).

        Returns:
            Валидированные данные (список файлов или один файл).
        """
        if isinstance(data, (list, tuple)):
            return [super().clean(file, initial) for file in data]
        return super().clean(data, initial)


class ProductForm(ModelForm):
    """
    Форма для создания и редактирования продукта.
    Поддерживает загрузку нескольких изображений.
    """

    class Meta:
        model = Product
        fields = ("name", "description", "price", "discount", "preview")

    images = MultipleImageField(
        widget=MultipleFileInput(attrs={"multiple": True}),
        required=False,
    )


class OrderForm(ModelForm):
    """
    Форма для создания и редактирования заказа.
    Позволяет выбрать несколько продуктов через чекбоксы.
    """

    class Meta:
        model = Order
        fields = (
            "user",
            "delivery_address",
            "promo_code",
        )

    products = ModelMultipleChoiceField(
        queryset=Product.objects.filter(archived=False),
        widget=CheckboxSelectMultiple
    )


class GroupForm(ModelForm):
    """
    Форма для создания и редактирования группы пользователей.
    """

    class Meta:
        model = Group
        fields = ("name",)
