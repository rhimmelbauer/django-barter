# Generated by Django 2.2.4 on 2019-08-06 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('sku', models.CharField(max_length=8, verbose_name='SKU')),
                ('msrp', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('usd', 'US Dollar')], max_length=4, verbose_name='Currency')),
                ('available', models.BooleanField(default=False, help_text='Is this currently available?', verbose_name='Available')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
