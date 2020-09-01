from django.utils.translation import gettext_lazy as _
from django.db import models

from iso4217 import Currency

###########
# CHOICES
###########

CURRENCY_CHOICES = [(c.name, c.value) for c in Currency ]

class PurchaseStatus(models.IntegerChoices):
    QUEUED = 1, _("Queued")
    ACTIVE = 2, _("Active")
    AUTHORIZED = 10, _("Authorized")
    CAPTURED = 15, _("Captured")
    COMPLETE = 20, _("Completed")
    CANCELED = 30, _("Canceled")
    REFUNDED = 35, _("Refunded")


class PaymentTypes(models.IntegerChoices):
    CREDIT_CARD = 10, _('Credit Card')
    BANK_ACCOUNT = 20, _('Bank Account')
    PAY_PAL = 30, _('Pay Pal')
    MOBILE = 40, _('Mobile')


class TransactionTypes(models.IntegerChoices):
    AUTHORIZE = 10, _('Authorize')
    CAPTURE = 20, _('Capture')
    SETTLE = 30, _('Settle')
    VOID = 40, _('Void')
    REFUND = 50, _('Refund')
