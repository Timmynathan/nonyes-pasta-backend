from django.core.management.base import BaseCommand

from store.models import Category, Product

PRODUCTS = [
    ("Nonye's Vercimelli Noodles and Chicken in Chilli Sauce", "Noodles", 6500),
    ("Nonye's Shrimp Alfredo Fettuccine Pasta", "Alfredo", 8500),
    ("Nonye's Beef Lasagna", "Lasagna", 7500),
    ("Nonye's Soup Dumpling Lasagna", "Lasagna", 8000),
    ("Nonye's Nigerian Mac n Cheese", "Mac n Cheese", 6000),
    ("Nonye's Alfredo Pasta", "Alfredo", 6500),
    ("Nonye's Vodka Rigatoni", "Rigatoni", 7000),
    ("Nonye's Stir-fry Pasta", "Stir-fry", 6500),
    ("Nonye's Native Pasta", "Native", 6000),
    ("Nonye's Suya & Veggie Jollof Spag", "Jollof Spag", 7000),
    ("Nonye's Sippin Pretty Mocktail", "Drinks", 3000),
    ("Nonye's Spicy Mojito", "Drinks", 3500),
]


class Command(BaseCommand):
    help = "Seed the 12 Nonye's Pasta menu items"

    def handle(self, *args, **options):
        for name, category_name, price in PRODUCTS:
            category, _ = Category.objects.get_or_create(name=category_name)
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": category,
                    "base_price": price,
                    "is_preorder": True,
                    "description": f"{name} - made fresh to order by Nonye's Pasta.",
                },
            )
            status = "created" if created else "already exists"
            self.stdout.write(f"{name}: {status}")
        self.stdout.write(self.style.SUCCESS("Done seeding products."))
