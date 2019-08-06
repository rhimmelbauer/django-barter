# Generated by Django 2.2.4 on 2019-08-06 01:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('usd', 'US Dollar')], max_length=4, verbose_name='Currency')),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name='Start Date')),
                ('end_date', models.DateTimeField(verbose_name='End Date')),
                ('priority', models.PositiveIntegerField(help_text='Higher number overrides prices with lower numbners in the same date range.', verbose_name='Priority')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_price', to='core.Product', verbose_name='Item')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('status', models.IntegerField(verbose_name='Status')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('price_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('usd', 'US Dollar')], max_length=4, verbose_name='Currency')),
                ('fullfilled', models.BooleanField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendor.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('site', models.ManyToManyField(help_text='Which site(s) is this inventory available to?', related_name='sites', to='sites.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_for_later', models.BooleanField()),
                ('items', models.ManyToManyField(to='core.Product', verbose_name='Items')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]