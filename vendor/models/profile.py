from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext as _

from .base import CreateUpdateModelBase
from .choice import CURRENCY_CHOICES
from .invoice import Invoice

#####################
# CUSTOMER PROFILE
#####################

class CustomerProfile(CreateUpdateModelBase):
    '''
    Additional customer information related to purchasing.
    This is what the Invoices are attached to.  This is abstracted from the user model directly do it can be mre flexible in the future.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, on_delete=models.SET_NULL, related_name="customer_profile")
    currency = models.CharField(_("Currency"), max_length=4, choices=CURRENCY_CHOICES, default=settings.DEFAULT_CURRENCY)      # User's default currency
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID, related_name="customer_profile")                      # For multi-site support

    class Meta:
        verbose_name = _("Customer Profile")
        verbose_name_plural = _("Customer Profiles")

    def __str__(self):
        return "{} Customer Profile".format(self.user.username)

    def get_cart(self):
        cart, created = self.invoices.get_or_create(status=Invoice.InvoiceStatus.CART)
        return cart
