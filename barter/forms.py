from calendar import monthrange
from datetime import datetime
from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import IntegerChoices
from django.forms import inlineformset_factory
from django.forms.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from .config import BARTER_PRODUCT_MODEL
from .models import Address, Offer, OrderItem, Price, Invoice
from .models.choice import PaymentTypes, TermType

Product = apps.get_model(BARTER_PRODUCT_MODEL)

        
class PriceForm(forms.ModelForm):
    start_date = forms.DateField(label=_("Start Date"), widget=SelectDateWidget())
    end_date = forms.DateField(label=_("End Date"), widget=SelectDateWidget())
    class Meta:
        model = Price
        fields = ['cost', 'currency', 'start_date', 'end_date', 'priority']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'site', 'available', 'description', 'meta']


class OfferForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(label=_("Available Products:"), required=True, queryset=Product.on_site.filter(available=True))
    start_date = forms.DateField(label=_("Start Date"), widget=SelectDateWidget())
    end_date = forms.DateField(label=_("End Date"), widget=SelectDateWidget())
    term_start_date = forms.DateField(label=_("Term Start Date"), widget=SelectDateWidget())

    class Meta:
        model = Offer
        fields = ['name', 'start_date', 'end_date', 'terms', 'term_details', 'term_start_date', 'available', 'offer_description', 'allow_multiple']

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['name']:
            product_names = [ product.name for product in self.cleaned_data['products'] ]
            if len(product_names) == 1:
                self.cleaned_data['name'] = product_names[0]
            else:
                self.cleaned_data['name'] = _("Bundle: ") + ", ".join(product_names)

        if self.data['terms'] == TermType.SUBSCRIPTION and not cleaned_data['term_details']:
            self.add_error('term_details', _("Invalid term details for subscription"))

        return cleaned_data


PriceFormSet = inlineformset_factory(
    Offer,
    Price,
    form=PriceForm,
    can_delete=True,
    exclude=('offer',),
    validate_max=True,
    min_num=1,
    extra=0)


class DateRangeForm(forms.Form):
    start_date = forms.DateField(required=False, label=_("Start Date"), widget=SelectDateWidget())
    end_date = forms.DateField(required=False, label=_("End Date"), widget=SelectDateWidget())

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and end_date < start_date:
            self.add_error('end_date', _('End Date cannot be before Start Date'))
            del(cleaned_data['end_date'])
            
        return cleaned_data

class CreateInvoiceForm(forms.Form):
    
