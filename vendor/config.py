# App Settings
from django.conf import settings

VENDOR_PRODUCT_MODEL = getattr(settings, "VENDOR_PRODUCT_MODEL", "vendor.Product")

VENDOR_PAYMENT_PROCESSOR = getattr(settings, "VENDOR_PAYMENT_PROCESSOR", "vendor.processor.base.PaymentProcessorBase")

DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", "usd")