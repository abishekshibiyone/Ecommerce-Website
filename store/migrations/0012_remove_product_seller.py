# Generated by Django 5.1.4 on 2025-01-22 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_product_seller'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='seller',
        ),
    ]
