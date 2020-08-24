import copy
import random
import string
import uuid
# import pycountry

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from address.models import AddressField
from autoslug import AutoSlugField
from iso4217 import Currency

##########
# CHOICES
##########


##########
# NestedModels
##########

# class MSRP(NestedModel):
#     pass


# https://en.wikipedia.org/wiki/ISO_4217
# CurrencyChoices.choices = [(int(cur.numeric), cur.name) for cur in pycountry.currencies]
# TODO: Moved to Django Enums/Choice objects

# REGION_TYPE_CHOICES = (
#                 (0, _("Country")), 
#                 (10, _("State/Province")), 
#                 (20, _("County")), 
#                 (30, _("City")), 
#             )


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
# BASE MODELS
##################

class CreateUpdateModelBase(models.Model):
    created = models.DateTimeField("date created", auto_now_add=True)
    updated = models.DateTimeField("last updated", auto_now=True)

    class Meta:
        abstract = True

# TODO: Validate multiple msrp lines
def validate_msrp_format(value):
    msrp = []
    if not value:
        return None

    msrp = value.split(',')

    if len(msrp) != 2 or not msrp:
        raise ValidationError(_("Invalid MSRP Value"), params={'value': value})
    
    if not msrp[0] or not msrp[1]:
        raise ValidationError(_("Invalid MSRP Value"), params={'value': value})

    if not msrp[0].lower() in Currency.__dict__:
        raise ValidationError(_("Invalid MSRP Value"), params={'value': value})

class ProductModelBase(CreateUpdateModelBase):
    '''
    This is the base class that all Products should inherit from.
    '''
    sku = models.CharField(_("SKU"), max_length=40, unique=True, blank=True, null=True, help_text=_("User Defineable SKU field"))   # Needs to be autogenerated by default, and unique from the PK
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)                                           # Used to track the product
    name = models.CharField(_("Name"), max_length=80, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID, related_name="products")        # For multi-site support
    slug = AutoSlugField(populate_from='name', unique_with='site__id')                                                                         # Gets set in the save
    available = models.BooleanField(_("Available"), default=False, help_text=_("Is this currently available?"))        # This can be forced to be unavailable if there is no prices attached.
    description = models.TextField(blank=True, null=True)
    meta = models.CharField(_("Meta"), max_length=150, validators=[validate_msrp_format], blank=True, null=True, help_text=_("Eg: USD,10.99\n(iso4217 Country Code), (MSRP Price)"))                                          # allows for things like a MSRP in multiple currencies. Not JSONField to force a db
    classification = models.ManyToManyField("vendor.TaxClassifier", blank=True)                                        # What taxes can apply to this item

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    # TODO: ADD trigger when object becomes unavailable to disable offer if it exisits. 

#########
# MIXINS
#########


#########
# TAXES
#########

# class TaxInfo(models.Model):
#     '''
#     This is meant to start with a simple sales tax estimation.
#     It will likely tie to someting from a 3rd party service, like Avalara eventually.
#     It will still indicate the type of product it is for tax purposes.
#     By default, they should only be set-up in the location where the business is run from.
#     '''
#     name = models.CharField(_("Name"), max_length=80, blank=True)
#     rate = models.FloatField()
#     currency = models.IntegerField(_("Currency"), choices=CurrencyChoices.choices)  # ISO 4217 Standard codes
#     start_date = models.DateTimeField(_("Start Date"), help_text="When should this tax rate start?")
#     description = models.TextField(_("Description"))
#     region_type = models.IntegerField(choices=REGION_TYPE_CHOICES)  # Where does this tax apply
#     region_name = models.CharField()


#####################
# Tax Classifier
#####################

class TaxClassifier(models.Model):
    '''
    This for things like "Digital Goods", "Furniture" or "Food" which may or
    may not be taxable depending on the location.  These are determined by the
    manager of all sites.
    '''
    name = models.CharField(_("Name"), max_length=80, blank=True)
    taxable = models.BooleanField()
    # info = models.ManyToManyField("vendor.TaxInfo")                 # Which taxes is this subject to and where.  This is for a more complex tax setup

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Product Classifier")
        verbose_name_plural = _("Product Classifiers")


#########
# OFFER
#########

class Offer(CreateUpdateModelBase):
    '''
    Offer attaches to a record from the designated VENDOR_PRODUCT_MODEL.  
    This is so more than one offer can be made per product, with different 
    priorities.
    '''
    class TermType(models.IntegerChoices):
        PERPETUAL = 0, _("Perpetual")
        SUBSCRIPTION = 10, _("Subscription")
        ONE_TIME_USER = 20, _("One-Time Use")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)                                # Used to track the product
    slug = AutoSlugField(populate_from='name', unique_with='site__id')                                               # SEO friendly 
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID, related_name="product_offers")                      # For multi-site support
    name = models.CharField(_("Name"), max_length=80, blank=True)                                           # If there is only a Product and this is blank, the product's name will be used, oterhwise it will default to "Bundle: <product>, <product>""
    product = models.ForeignKey(settings.VENDOR_PRODUCT_MODEL, on_delete=models.CASCADE, related_name="offers", blank=True, null=True)         # TODO: Combine with bundle field?
    bundle = models.ManyToManyField(settings.VENDOR_PRODUCT_MODEL, related_name="bundles", blank=False)  # Used in the case of a bundles/packages.  Bundles override individual products
    start_date = models.DateTimeField(_("Start Date"), help_text="What date should this offer become available?")
    end_date = models.DateTimeField(_("End Date"), blank=True, null=True, help_text="Expiration Date?")
    terms =  models.IntegerField(_("Terms"), default=0, choices=TermType.choices)
    term_details = models.JSONField(_("Details"), default=dict, blank=True, null=True)
    term_start_date = models.DateTimeField(_("Term Start Date"), help_text="When is this product available to use?", blank=True, null=True) # Useful for Event Tickets or Pre-Orders
    available = models.BooleanField(_("Available"), default=False, help_text="Is this currently available?")

    class Meta:
        verbose_name = _("Offer")
        verbose_name_plural = _("Offers")

    def __str__(self):
        return self.name

    def current_price(self):
        '''
        Check if there are any price options active, otherwise use msrp.
        '''
        now = timezone.now()
        price_before_tax, price_after_tax = 0, 0
        
        if self.prices.all().count() == 0:                                                         # Check if offer has prices
            price_before_tax = float(self.product.meta.split(',')[1])# TODO: Implement MSRP from product/bundles                        # No prices default to product MSRP
        else:
            if self.prices.filter(start_date__lte=now):                         # Check if offer start date is less than or equal to now
                if self.prices.filter(start_date__lte=now, end_date__gte=now):  # Check if is between two start and end date. return depending on priority
                    price_before_tax = self.prices.filter(start_date__lte=now, end_date__gte=now).order_by('priority').last().cost
                else:                                                           # Return acording to start date and priority
                    price_before_tax = self.prices.filter(start_date__lte=now).order_by('priority').last().cost
            else:                
                # TODO: need to validate if it is a bundle                        # Only future start date. Default to MSRP
                if self.product.meta:
                    price_before_tax = float(self.product.meta.split(',')[1]) # TODO: Implement MSRP from product with country code 
                else:                    
                    raise FieldError(_("There is no price set on Offer or MSRP on Product"))
        
        # price_after_tax = price_before_tax * self.product.tax_classifier.tax_rule.tax   TODO: implement tax_classifier and tax rule and bundle
        price_after_tax = price_before_tax
        
        return price_after_tax

    def add_to_cart_link(self):
        return reverse("vendor:add-to-cart", kwargs={"slug":self.slug})

    def remove_from_cart_link(self):
        return reverse("vendor:remove-from-cart", kwargs={"slug":self.slug})


class Price(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="prices")
    cost = models.FloatField(blank=True, null=True)
    currency = models.CharField(_("Currency"), max_length=4, choices=[(c.name, c.value) for c in Currency ], default=settings.DEFAULT_CURRENCY)
    start_date = models.DateTimeField(_("Start Date"), help_text="When should the price first become available?")
    end_date = models.DateTimeField(_("End Date"), blank=True, null=True, help_text="When should the price expire?")
    priority = models.IntegerField(_("Priority"), help_text="Higher number takes priority", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.priority:       # TODO: Add check to see if this is the only price on the offer, then let it be 0.  If not, might need to do some assumptions to guess what it should be.
            self.priority = 0

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")

    def __str__(self):
        return "{} for {}:{}".format(self.offer.name, Currency[self.currency].value, self.cost)


class CustomerProfile(CreateUpdateModelBase):
    '''
    Additional customer information related to purchasing.
    This is what the Invoices are attached to.  This is abstracted from the user model directly do it can be mre flexible in the future.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, on_delete=models.SET_NULL, related_name="customer_profile")
    currency = models.CharField(_("Currency"), max_length=4, choices=[(c.name, c.value) for c in Currency ], default=settings.DEFAULT_CURRENCY)      # User's default currency
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID, related_name="customer_profile")                      # For multi-site support

    class Meta:
        verbose_name = _("Customer Profile")
        verbose_name_plural = _("Customer Profiles")

    def __str__(self):
        return "{} Customer Profile".format(self.user.username)

    def get_cart(self):
        cart, created = self.invoices.get_or_create(status=Invoice.InvoiceStatus.CART)
        return cart


class Address(models.Model):
    name = models.CharField(_("Name"), max_length=80, blank=True)                                           # If there is only a Product and this is blank, the product's name will be used, oterhwise it will default to "Bundle: <product>, <product>""
    profile = models.ForeignKey(CustomerProfile, verbose_name=_("Customer Profile"), null=True, on_delete=models.CASCADE, related_name="addresses")
    address = AddressField()


class Invoice(CreateUpdateModelBase):
    '''
    An invoice starts off as a Cart until it is puchased, then it becomes an Invoice.
    '''
    class InvoiceStatus(models.IntegerChoices):
        CART = 0, _("Cart")             # total = subtotal = sum(OrderItems.Offer.Price + Product.TaxClassifier). Avalara
        CHECKOUT = 10, _("Checkout")    # total = subtotal + shipping + Tax against Addrr if any.
        QUEUED = 20, _("Queued")        # Queued to for Payment Processor.
        PROCESSING = 30, _("Processing")# Payment Processor update, start of payment.
        FAILED = 40, _("Failed")        # Payment Processor Failed Transaction.
        COMPLETE = 50, _("Complete")    # Payment Processor Completed Transaction.
        REFUNDED = 60, _("Refunded")    # Invoice Refunded to client. 

    profile = models.ForeignKey(CustomerProfile, verbose_name=_("Customer Profile"), null=True, on_delete=models.CASCADE, related_name="invoices")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID, related_name="invoices")                      # For multi-site support
    status = models.IntegerField(_("Status"), choices=InvoiceStatus.choices, default=InvoiceStatus.CART)
    customer_notes = models.TextField(blank=True, null=True)
    vendor_notes = models.TextField(blank=True, null=True)
    ordered_date = models.DateTimeField(_("Ordered Date"), blank=True, null=True)               # When was the purchase made?
    subtotal = models.FloatField(default=0.0)                                   
    tax = models.FloatField(blank=True, null=True)                              # Set on checkout
    shipping = models.FloatField(blank=True, null=True)                         # Set on checkout
    total = models.FloatField(blank=True, null=True)                            # Set on purchase
    currency = models.CharField(_("Currency"), max_length=4, choices=[(c.name, c.value) for c in Currency ], default=settings.DEFAULT_CURRENCY)      # User's default currency
    shipping_address = models.ForeignKey(Address, verbose_name=_("Shipping Address"), on_delete=models.CASCADE, blank=True, null=True)
    # paid = models.BooleanField(_("Paid"))                 # May be Useful for quick filtering on invoices that are outstanding
    # paid_date = models.DateTimeField(_("Payment Date"))

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def __str__(self):
        return "%s Invoice (%s)" % (self.profile.user.username, self.created.strftime('%Y-%m-%d %H:%M'))

    def add_offer(self, offer):
        order_item, created = self.order_items.get_or_create(offer=offer)
        # make sure the invoice pk is also in the OriderItem
        if not created:
            order_item.quantity += 1
            order_item.save()

        self.update_totals()
        self.save()
        return order_item

    def remove_offer(self, offer):
        try:
            order_item = self.order_items.get(offer=offer)      # Get the order item if it's present
        except:
            return 0

        order_item.quantity -= 1

        if order_item.quantity == 0:
            order_item.delete()
        else:
            order_item.save()

        self.update_totals()
        self.save()
        return order_item

    def calculate_shipping(self):
        '''
        Based on the Shipping Address
        '''
        self.shipping = 0

    def calculate_tax(self):
        '''
        Extendable
        '''
        self.tax = 0

    def update_totals(self):
        self.subtotal = sum([item.total for item in self.order_items.all() ])

        self.calculate_shipping()
        self.calculate_tax()
        self.total = self.subtotal + self.tax + self.shipping


    # def save(self):
    #     pass
    # DEFAULT_CURRENCY


class OrderItem(CreateUpdateModelBase):
    '''
    A link for each item to a user after it's been purchased
    '''
    invoice = models.ForeignKey(Invoice, verbose_name=_("Invoice"), on_delete=models.CASCADE, related_name="order_items")
    offer = models.ForeignKey(Offer, verbose_name=_("Offer"), on_delete=models.CASCADE, related_name="order_items")
    quantity = models.IntegerField(_("Quantity"), default=1)

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return "%s - %s" % (self.invoice.profile.user.username, self.offer.name)

    @property
    def total(self):
        return self.quantity * self.price

    @property
    def price(self):
        return self.offer.current_price()

    @property
    def name(self):
        # TODO: What if it is an Bundle
        return self.offer.product.name


class Payment(models.Model):
    '''
    Payments
    - Payments are typically from a Credit Card, PayPal or ACH
    - Multiple Payments can be applied to an invoice
    - Gift cards can be used as payments
    - Discounts are Payment credits
    '''
    invoice = models.ForeignKey(Invoice, verbose_name=_("Invoice"), on_delete=models.CASCADE, related_name="payments")
    created = models.DateTimeField("date created", auto_now_add=True)
    transaction = models.CharField(_("Transaction ID"), max_length=50)
    provider = models.CharField(_("Payment Provider"), max_length=16)
    amount = models.FloatField(_("Amount"))
    profile = models.ForeignKey(CustomerProfile, verbose_name=_("Purchase Profile"), blank=True, null=True, on_delete=models.SET_NULL, related_name="payments")
    billing_address = models.ForeignKey(Address, verbose_name=_("payments"), on_delete=models.CASCADE, blank=True, null=True)
    result = models.TextField(_("Result"), blank=True, null=True)
    success = models.BooleanField(_("Successful"), default=False)


class Reciept(CreateUpdateModelBase):
    '''
    A link for all the purchases a user has made. Contains subscription start and end date.
    This is generated for each item a user purchases so it can be checked in other code.
    '''
    class RecieptStatus(models.IntegerChoices):
        QUEUED = 0, _("Queued") 
        PROCESSING = 10, _("Processing")
        EXPIRED = 20, _("Expired")
        HOLD = 30, _("Hold")
        CANCELED = 40, _("Canceled") 
        REFUNDED = 50, _("Refunded") 
        COMPLETED = 60, _("Completed")
    profile = models.ForeignKey(CustomerProfile, verbose_name=_("Purchase Profile"), null=True, on_delete=models.CASCADE, related_name="reciepts")
    order_item = models.ForeignKey('vendor.OrderItem', verbose_name=_("Order Item"), on_delete=models.CASCADE, related_name="reciepts")
    product = models.ForeignKey(settings.VENDOR_PRODUCT_MODEL, on_delete=models.CASCADE, related_name="reciepts", blank=True, null=True)           # TODO:  Goal is to make it easier to check to see if a user owns the product. WHAT IF IT IS A BUNDLE
    start_date = models.DateTimeField(_("Start Date"), blank=True, null=True)
    end_date = models.DateTimeField(_("End Date"), blank=True, null=True)
    auto_renew = models.BooleanField(_("Auto Renew"), default=False)        # For subscriptions
    vendor_notes = models.TextField()
    transaction = models.CharField(_("Transaction"), max_length=80)
    status = models.IntegerField(_("Status"), choices=RecieptStatus.choices, default=0)       # Fulfilled, Refund
    class Meta:
        verbose_name = _("Reciept")
        verbose_name_plural = _("Reciepts")

    def __str__(self):
        return "%s - %s - %s" % (self.profile.user.username, self.order_item.offer.name, self.created.strftime('%Y-%m-%d %H:%M'))


class Wishlist(models.Model):
    profile = models.ForeignKey(CustomerProfile, verbose_name=_("Purchase Profile"), null=True, on_delete=models.CASCADE, related_name="wishlists")
    name = models.CharField(_("Name"), max_length=100, blank=False)

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")

    def __str__(self):
        return self.name


class WishlistItem(CreateUpdateModelBase):
    '''
    
    '''
    wishlist = models.ForeignKey(Wishlist, verbose_name=_("Wishlist"), on_delete=models.CASCADE, related_name="wishlist_items")
    offer = models.ForeignKey(Offer, verbose_name=_("Offer"), on_delete=models.CASCADE, related_name="wishlist_items")

    class Meta:
        verbose_name = _("Wishlist Item")
        verbose_name_plural = _("Wishlist Items")
        # TODO: Unique Name Per User

    def __str__(self):
        return "({}) {}: {}".format(self.wishlist.profile.user.username, self.wishlist.name, self.offer.name)


# class Discount(models.Model):
#     pass


# class GiftCode(models.Model):
#     pass


############
# SIGNALS
############

# post_save.connect(create_price_object, sender=Offer, dispatch_uid="create_price_object")
