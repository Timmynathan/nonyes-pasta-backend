from django.db import migrations


def flag_mainland(apps, schema_editor):
    DeliveryLocation = apps.get_model('orders', 'DeliveryLocation')
    DeliveryLocation.objects.filter(group__icontains='Mainland').update(
        arrange_privately=True, fee=0,
    )


def unflag_mainland(apps, schema_editor):
    DeliveryLocation = apps.get_model('orders', 'DeliveryLocation')
    DeliveryLocation.objects.filter(group__icontains='Mainland').update(
        arrange_privately=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_deliverylocation_arrange_privately_and_more'),
    ]

    operations = [
        migrations.RunPython(flag_mainland, unflag_mainland),
    ]
