"""
Run this once to migrate all local categories, products, and images to the live database.
Usage:
    DATABASE_URL="<render external url>" python migrate_to_live.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import cloudinary
import cloudinary.uploader
from decouple import config
from store.models import Category, Product

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
)

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

CATEGORIES = [
    {'name': 'Alfredo',     'slug': 'alfredo'},
    {'name': 'Lasagna',     'slug': 'lasagna'},
    {'name': 'Rigatoni',    'slug': 'rigatoni'},
    {'name': 'Stir-fry',    'slug': 'stir-fry'},
    {'name': 'Native',      'slug': 'native'},
    {'name': 'Jollof Spag', 'slug': 'jollof-spag'},
    {'name': 'Linguine',    'slug': 'linguine'},
    {'name': 'Healthy',     'slug': 'healthy'},
    {'name': 'Non-Pasta',   'slug': 'non-pasta'},
    {'name': 'Protein',     'slug': 'protein'},
    {'name': 'Drinks',      'slug': 'drinks'},
    {'name': 'Noodles',     'slug': 'noodles'},
    {'name': 'Mac n Cheese','slug': 'mac-n-cheese'},
]

PRODUCTS = [
    {'name': "Nonye's Penne Alfredo Pasta",                      'category': 'alfredo',    'price': 8000,  'slug': 'nonyes-penne-alfredo-pasta',                      'image': 'products/alfredo_pasta.png'},
    {'name': "Nonye's Shrimp Alfredo Fettuccine Pasta",          'category': 'alfredo',    'price': 12500, 'slug': 'nonyes-shrimp-alfredo-fettuccine-pasta',          'image': 'products/shrimp_alfredo_pasta.png'},
    {'name': "Nonye's Beef Lasagna",                             'category': 'lasagna',    'price': 10500, 'slug': 'nonyes-beef-lasagna',                             'image': 'products/beef_lasagna.png'},
    {'name': "Nonye's Vodka Rigatoni",                           'category': 'rigatoni',   'price': 9500,  'slug': 'nonyes-vodka-rigatoni',                           'image': 'products/vodka_rigatoni.png'},
    {'name': "Nonye's Stir-fry Pasta",                           'category': 'stir-fry',   'price': 7500,  'slug': 'nonyes-stir-fry-pasta',                           'image': 'products/stirfry_pasta.png'},
    {'name': "Nonye's Nigerian Native Spaghetti",                'category': 'native',     'price': 7500,  'slug': 'nonyes-nigerian-native-spaghetti',                'image': 'products/native_pasta.png'},
    {'name': "Nonye's Suya Jollof Spag",                         'category': 'jollof-spag','price': 7000,  'slug': 'nonyes-suya-jollof-spag',                         'image': 'products/suya_jollof_spaggeti.png'},
    {'name': "Nonye's Tomato Shrimp Linguine",                   'category': 'linguine',   'price': 11000, 'slug': 'nonyes-tomato-shrimp-linguine',                   'image': 'products/tomato_shrimp.png'},
    {'name': "Nonye's Pasta Salad",                              'category': 'healthy',    'price': 6500,  'slug': 'nonyes-pasta-salad',                              'image': 'products/pasta_salad.png'},
    {'name': "Nonye's Nigerian Mac n Cheese",                    'category': 'mac-n-cheese','price': 6000, 'slug': 'nonyes-nigerian-mac-n-cheese',                    'image': 'products/mac_cheese.JPG'},
    {'name': "Nonye's Asun & Bacon Loaded Potatoes",             'category': 'non-pasta',  'price': 9500,  'slug': 'nonyes-asun-bacon-loaded-potatoes',               'image': 'products/Loaded-Bacon-Cheese-Fries-3-773x900.jpg'},
    {'name': "Nonye's Asun Jollof Bowl",                         'category': 'non-pasta',  'price': 12500, 'slug': 'nonyes-asun-jollof-bowl',                         'image': 'products/asun_jollof.png'},
    {'name': "Nonye's Crispy Drumstick",                         'category': 'protein',    'price': 2500,  'slug': 'nonyes-crispy-drumstick',                         'image': 'products/chrunchy-Fried-Chicken-Drumsticks-5.webp'},
    {'name': "Nonye's Grilled Chicken Lap",                      'category': 'protein',    'price': 4000,  'slug': 'nonyes-grilled-chicken-lap',                      'image': 'products/grilled chicken lap.jpg'},
    {'name': "Nonye's Grilled Turkey",                           'category': 'protein',    'price': 3000,  'slug': 'nonyes-grilled-turkey',                           'image': 'products/grilled_turkey.jpg'},
    {'name': "Nonye's Sippin Pretty Mocktail",                   'category': 'drinks',     'price': 5000,  'slug': 'nonyes-sippin-pretty-mocktail',                   'image': 'products/sipping_pretty.jpeg'},
    {'name': "Nonye's Spicy Mojito",                             'category': 'drinks',     'price': 8000,  'slug': 'nonyes-spicy-mojito',                             'image': 'products/spicy_mojito.jpg'},
    {'name': "Nonye's Vercimelli Noodles and Chicken in Chilli Sauce", 'category': 'noodles', 'price': 6500, 'slug': 'nonyes-vercimelli-noodles-and-chicken-in-chilli-sauce', 'image': ''},
]


def upload_image(image_path):
    if not image_path:
        return ''
    local_path = os.path.join(MEDIA_ROOT, image_path)
    if not os.path.exists(local_path):
        print(f"  ⚠ Image not found locally: {local_path}")
        return ''
    print(f"  ↑ Uploading {image_path} to Cloudinary...")
    result = cloudinary.uploader.upload(local_path, folder='nonyes-pasta')
    return result['public_id']


def run():
    print("=== Creating categories ===")
    cat_map = {}
    for c in CATEGORIES:
        obj, created = Category.objects.get_or_create(slug=c['slug'], defaults={'name': c['name']})
        cat_map[c['slug']] = obj
        print(f"  {'Created' if created else 'Exists'}: {c['name']}")

    print("\n=== Creating products & uploading images ===")
    for p in PRODUCTS:
        if Product.objects.filter(slug=p['slug']).exists():
            print(f"  Exists: {p['name']}")
            continue

        cloudinary_id = upload_image(p['image'])

        Product.objects.create(
            name=p['name'],
            slug=p['slug'],
            category=cat_map.get(p['category']),
            base_price=p['price'],
            image=cloudinary_id,
        )
        print(f"  ✓ Created: {p['name']}")

    print("\n✅ Done! All products are live.")


if __name__ == '__main__':
    run()
