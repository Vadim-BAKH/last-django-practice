
from django.core.management import BaseCommand
from django.db.models import Count, Sum

from shop.models import Order


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregate")
        # result = Product.objects.filter(
        #     Q(name__contains="Кофе 1") | Q(name__contains="Кофе 2") | Q(name__contains="Кофе 3")
        # ).aggregate(
        #     Avg("price"),
        #     Min("price"),
        #     max_price=Max("price"),
        #     count=Count("id"),
        # )
        # print(result)
        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products"),
        )
        for order in orders:
            print(
                f"Order # {order.id} "
                f"with {order.products_count}"
                f"products worth {order.total}"
            )
        self.stdout.write("Done")
