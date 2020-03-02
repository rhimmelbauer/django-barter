import uuid
import random
import string

from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.utils.text import slugify

from jsonfield import JSONField

#############
# CURRENCIES
#############

CURRENCIES = {  'usd': {
                    'name': _('US Dollar'),
                    'symbol':"$"},
                # 'euro': {
                #     'name': _('Euros'),
                #     'symbol':"E"},
                # }
            }

##########
# CHOICES
##########

clist = list(CURRENCIES.keys())
clist.sort()

CURRENCY_CHOICES = tuple([(item, CURRENCIES[item]['name']) for item in clist])        #(('usd', _('US Dollar')),)

ORDER_STATUS_CHOICES = (
                (0, _("Cart")), 
                (10, _("Wishlist")), 
                (20, _("Processing")), 
                (30, _("Failed")), 
                (40, _("Complete")) 
            )

LICENSE_TYPE_CHOICES = ((0, _("Perpetual")), (10, _("Subscription")) )

PURCHASE_STATUS_CHOICES = (
                (0, _("Queued")), 
                (10, _("Active")), 
                (20, _("Expired")), 
                (30, _("Canceled")), 
                (40, _("Refunded")), 
                (50, _("Completed")) 
            )

############
# UTILITIES
############

def random_string(length=8, check=[]):
    letters= string.digits + string.ascii_uppercase
    value = ''.join(random.sample(letters,length))

    if value not in check:
        return value
    return random_string(length=length, check=check)

def generate_sku():
    return random_string()


##################
# ABSTRACT MODELS
##################

class CreateUpdateModelBase(models.Model):
    created = models.DateTimeField("date created", auto_now_add=True)
    updated = models.DateTimeField("last updated", auto_now=True)

    class Meta:
        abstract = True

#########
# MIXINS
#########


#########
# SIGNAL
#########

# def create_price_object(sender, instance, **kwargs):
#     if not instance.sale_price.all().count():
#         Price.objects.create(
#             offer=instance,
#             cost=instance.msrp,
#             currency = instance.currency,
#             start_date = timezone.now(),
#             end_date = timezone.now() + timezone.timedelta(days=10),    # 
#             priority = 1
#         )


#########
# OFFER
#########

class ProductOffer(CreateUpdateModelBase):
    '''
    Product Offer attaches to a record from the designated PRODUCT_MODEL.  
    This is so more than one offer can be made per product, with different 
    priorities.
    '''
    sku = models.CharField(_("SKU"), max_length=40, help_text="User Defineable SKU field" )                 # Needs to be autogenerated by default, and unique from the PK
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)                                # Used to track the product
    name = models.CharField(_("Name"), max_length=100, blank=True)
    slug = models.SlugField(_("Slug"))
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID)
    product = models.ForeignKey(settings.PRODUCT_MODEL, verbose_name=_("Product"), on_delete=models.CASCADE, related_name="product_offer", blank=True, null=True)
    msrp = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    currency = models.CharField(_("Currency"), max_length=4, choices=CURRENCY_CHOICES)
    license_type =  models.IntegerField(_("License_Type"), default=0, choices=LICENSE_TYPE_CHOICES)
    cost = models.DecimalField(_("Cost"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=4, choices=CURRENCY_CHOICES)
    start_date = models.DateTimeField(_("Start Date"), help_text="What date should this product be made available?")
    end_date = models.DateTimeField(_("End Date"), null=True, help_text="Expiration Date?")
    priority = models.PositiveIntegerField(_("Priority"), help_text="Higher number overrides prices with lower numbers in the same date range.")
    available = models.BooleanField(_("Available"), default=False, help_text="Is this currently available?")

    class Meta:
        verbose_name = _("Product Offer")
        verbose_name_plural = _("Product Offers")

    def current_price(self):
        '''
        Check if there are any price options active, otherwise use msrp.
        '''
        try:
            price = self.sale_price.filter( start_date__lte=timezone.now(), end_date__gte=timezone.now() ).order_by('priority').first().cost
            return price
        except:
            return self.msrp

    def current_price_and_expiration(self):
        price = self.sale_price.filter( start_date__lte=timezone.now(), end_date__gte=timezone.now() ).order_by('priority').first()
        return price.cost, price.end_date

    def price_display(self):
        return "$%s" % self.current_price()

    def __str__(self):
        return self.name
       
    def save(self, *args, **kwargs):

        if not self.name:      
            self.name = "%s" % (self.product.name)

        self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def add_to_cart_link(self):
        return reverse("vendor-new-add-to-cart", kwargs={"sku":self.sku})


class Invoice(CreateUpdateModelBase):
    '''
    An invoice starts off as a Cart until it is puchased, then it becomes an Invoice.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, on_delete=models.SET_NULL)
    status = models.IntegerField(_("Status"), choices=ORDER_STATUS_CHOICES, default=0)
    ordered_date = models.DateField(_("Ordered Date"), null=True)
    attrs = JSONField(_("attrs"), blank=True, null=True)

    def __str__(self):
        return "%s - (%s)" % (self.user.username, self.created.strftime('%Y-%m-%d %H:%M'))


class OrderItem(CreateUpdateModelBase):
    '''
    A link for each item to a user after it's been purchased
    '''
    invoice = models.ForeignKey(Invoice, verbose_name=_("Invoice"), on_delete=models.CASCADE, related_name="order_items")
    offer = models.ForeignKey(ProductOffer, verbose_name=_("Offer"), on_delete=models.CASCADE, related_name="items")
    # price_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)                              # This is blank until a purchase is made? or should it be included in the reciept?
    # currency = models.CharField(_("Currency"), max_length=4, choices=CURRENCY_CHOICES)
    # fullfilled = models.BooleanField(default=False)
    quantity = models.IntegerField(_("Quantity"), default=1)
    # gift = models.BooleanField(default=False)

    def total(self):
        return self.quantity * self.price.cost

    def __str__(self):
        return "%s - %s" % (self.invoice.user.username, self.offer.name)

    @property
    def price(self):
        return self.offer.current_price()

    @property
    def total(self):
        return self.price * self.quantity

    @property
    def product_name(self):
        return self.offer.product.name


# class Purchase(CreateUpdateModelBase):          # todo: Rename to Reciept?
#     '''
#     A link for all the purchases a user has made. Contains subscription start and end date.
#     '''

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, on_delete=models.SET_NULL)
#     order_item = models.ForeignKey('vendor.OrderItem', verbose_name=_("Order Item"), on_delete=models.CASCADE, related_name="purchases")
#     product = models.ForeignKey(settings.PRODUCT_MODEL, verbose_name=_("Product"), on_delete=models.CASCADE)
#     start_date = models.DateTimeField(_("Start Date"), blank=True, null=True)
#     end_date = models.DateTimeField(_("End Date"), blank=True, null=True)
#     auto_renew = models.BooleanField(_("Auto Renew"), default=False)
#     status = models.IntegerField(_("Status"), choices=PURCHASE_STATUS_CHOICES, default=0)

#     class Meta:
#         verbose_name_plural = "purchases"

#     def __str__(self):
#         return "%s - %s - %s" % (self.user.username, self.product.name, self.created.strftime('%Y-%m-%d %H:%M'))


# class CustomerProfile(CreateUpdateModelBase):
#     '''
#     Additional customer information related to purchasing.
#     '''

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, on_delete=models.SET_NULL)
#     currency = models.CharField(_("Currency"), max_length=4, choices=CURRENCY_CHOICES)
#     attrs = JSONField(_("attrs"), blank=True, null=True)

#     def __str__(self):
#         return "%s" % (self.user.username)


# class Refund(CreateUpdateModelBase):
    
#     purchase = models.ForeignKey('vendor.Purchase', verbose_name=_("Purchase"), on_delete=models.CASCADE, related_name="refunds")
#     reason = models.CharField(_("Reason"), max_length=400)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, on_delete=models.SET_NULL)
#     accepted = models.BooleanField(_("Accepted"), default=False)

# class Library(CreateUpdateModelBase):
#     '''
#     A list of all the items a user owns.
#     '''
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
#     items = models.ManyToManyField(settings.PRODUCT_MODEL, verbose_name=_("Items"))


# class Wishlist(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
#     name = models.CharField(_("Name"), max_length=100, blank=False)
#     items = models.ManyToManyField(settings.PRODUCT_MODEL, verbose_name=_("Items"))


# class Discount(models.Model):
#     pass


# class GiftCode(models.Model):
#     pass


############
# SIGNALS
############

# post_save.connect(create_price_object, sender=Offer, dispatch_uid="create_price_object")
