# Generated by Django 2.2.4 on 2019-08-10 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_product_uuid'),
        ('vendor', '0004_auto_20190810_2230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='item',
        ),
        migrations.AddField(
            model_name='price',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sale_price', to='core.Product', verbose_name='Product'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.Product'),
        ),
    ]
