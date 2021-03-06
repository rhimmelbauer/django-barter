# Generated by Django 3.1.4 on 2020-12-26 18:59

import autoslug.fields
import barter.models.base
import barter.models.validator
import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('barter', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('sku', models.CharField(blank=True, help_text='User Defineable SKU field', max_length=40, null=True, unique=True, verbose_name='SKU')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name', unique_with=('site__id',))),
                ('available', models.BooleanField(default=False, help_text='Is this currently available?', verbose_name='Available')),
                ('description', models.JSONField(blank=True, default=barter.models.base.product_description_default, help_text="Eg: {'call out': 'The ultimate product'}", null=True, verbose_name='Description')),
                ('meta', models.JSONField(blank=True, default=barter.models.base.product_meta_default, help_text="Eg: { 'msrp':{'usd':10.99} }\n(iso4217 Country Code):(MSRP Price)", null=True, validators=[barter.models.validator.validate_msrp], verbose_name='Meta')),
                ('classification', models.ManyToManyField(blank=True, to='barter.TaxClassifier')),
                ('offers', models.ManyToManyField(blank=True, related_name='products', to='barter.Offer')),
                ('receipts', models.ManyToManyField(blank=True, related_name='products', to='barter.Receipt')),
                ('site', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='sites.site', verbose_name='Site')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=80, verbose_name='Name')),
                ('site', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sites.site')),
            ],
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
