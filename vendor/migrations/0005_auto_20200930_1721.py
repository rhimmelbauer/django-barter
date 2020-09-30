# Generated by Django 3.1 on 2020-09-30 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0004_offer_offer_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='First Name'),
        ),
        migrations.AddField(
            model_name='address',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='address',
            name='address_1',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Address 1'),
        ),
        migrations.AlterField(
            model_name='address',
            name='locality',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='address',
            name='postal_code',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Postal Code'),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='State'),
        ),
    ]
