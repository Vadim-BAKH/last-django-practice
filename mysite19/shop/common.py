from ast import literal_eval
from csv import DictReader
from io import TextIOWrapper

from django.db import transaction

from shop.models import Order, Product


def save_csv_products(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row, created_by=user)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products

def save_csv_orders(file, encoding, user):
    csv_file = TextIOWrapper(file, encoding=encoding)
    reader = DictReader(csv_file)
    with transaction.atomic():
        for row in reader:
            order_data = {
                "delivery_address": row.get("delivery_address", ""),
                "promo_code": row.get("promo_code", ""),
                "user": user,
            }

            try:
                products_str = row.get("products", "[]")
                products_ids = literal_eval(products_str)
                if not isinstance(products_ids, list):
                    products_ids = []
            except (SyntaxError, ValueError):
                products_ids = []

            order = Order.objects.create(**order_data)

            if products_ids:
                products = Product.objects.filter(pk__in=products_ids)
                order.products.set(products)
