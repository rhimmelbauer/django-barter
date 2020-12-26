# App Settings
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

BARTER_PRODUCT_MODEL = getattr(settings, "BARTER_PRODUCT_MODEL", "barter.Product")

BARTER_PAYMENT_PROCESSOR = getattr(settings, "BARTER_PAYMENT_PROCESSOR", "dummy.DummyProcessor")

DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", "usd")

AVAILABLE_CURRENCIES = getattr(settings, "AVAILABLE_CURRENCIES", {'usd': _('USD Dollars')})

BARTER_STATE = getattr(settings, "BARTER_STATE", "DEBUG")

# Encryption settings
BARTER_DATA_ENCODER = getattr(settings, "BARTER_DATA_ENCODER", "barter.encrypt.cleartext")
