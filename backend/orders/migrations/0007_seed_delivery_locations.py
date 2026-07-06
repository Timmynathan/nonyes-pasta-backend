from django.db import migrations
from orders.delivery import DELIVERY_ZONES


def seed(apps, schema_editor):
    DeliveryLocation = apps.get_model('orders', 'DeliveryLocation')
    for gi, zone in enumerate(DELIVERY_ZONES):
        for si, (name, fee) in enumerate(zone['locations']):
            DeliveryLocation.objects.update_or_create(
                name=name,
                defaults={
                    'group': zone['group'],
                    'fee': fee,
                    'group_order': gi,
                    'sort_order': si,
                    'is_active': True,
                },
            )


def unseed(apps, schema_editor):
    apps.get_model('orders', 'DeliveryLocation').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_deliverylocation'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
