# Generated by Django 2.2.4 on 2019-08-10 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0003_auto_20190810_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'Cart'), (10, 'Processing'), (20, 'Complete')], default=0, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='fullfilled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
