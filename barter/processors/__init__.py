from barter.config import BARTER_PAYMENT_PROCESSOR
from django.utils.module_loading import import_string

PaymentProcessor = import_string('barter.processors.{}'.format(BARTER_PAYMENT_PROCESSOR))