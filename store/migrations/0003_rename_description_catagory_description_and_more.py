# Generated by Django 5.1.4 on 2025-01-15 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_product_catagory_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='catagory',
            old_name='Description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='catagory_name',
            new_name='category',
        ),
        migrations.AlterField(
            model_name='catagory',
            name='status',
            field=models.BooleanField(default=False, help_text='0-Show, 1-Hidden'),
        ),
    ]
