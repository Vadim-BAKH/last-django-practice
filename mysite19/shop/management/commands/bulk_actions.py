
from django.core.management import BaseCommand

from shop.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        # user = User.objects.get(username="admin")
        self.stdout.write("Start demo bulk actions")

        result = Product.objects.filter(
            name__contains="Кофе 1",
        ).update(discount=20)
        print(result)
        # info = [
        #     ("Кофе 1", 200),
        #     ("Кофе 2", 250),
        #     ("Кофе 3", 300),
        # ]
        # products = [
        #     Product(name=name, price=price, created_by=user)
        #     for name, price in info
        # ]
        # result = Product.objects.bulk_create(products)
        # for res in result:
        #     print(res)
        self.stdout.write("Done")
