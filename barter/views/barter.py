from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext

from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView, View, FormView

from iso4217 import Currency

from barter.models import Offer, Invoice, Payment, Address, CustomerProfile, OrderItem, Receipt
from barter.models.choice import TermType, PurchaseStatus
from barter.models.utils import set_default_site_id
from barter.processors import PaymentProcessor
from barter.forms import InvoiceForm


# The Payment Processor configured in settings.py
payment_processor = PaymentProcessor

# TODO: Need to remove the login required

def get_purchase_invoice(user):
    """
    Return an invoice that is in checkout or cart state or a newly create invoice in cart state.
    """
    profile, created = user.customer_profile.get_or_create(site=settings.SITE_ID)
    return profile.get_cart_or_checkout_cart()

def clear_session_purchase_data(request):
    if 'billing_address_form' in request.session:
        del(request.session['billing_address_form'])
    if 'credit_card_form' in request.session:
        del(request.session['credit_card_form'])

def get_or_create_session_cart(session):
    session_cart = {}
    if 'session_cart' not in session:
        session['session_cart'] = session_cart
    session_cart = session.get('session_cart')

    return session_cart
    
def check_offer_items_or_redirect(invoice, request):
    
    if invoice.order_items.count() < 1:
        messages.info(request, _("Please add to your cart"))
        redirect('barter:cart')

class InvoiceListView(ListView):
    '''
    View all pending invoices to be delievered
    '''
    model = Invoice
    queryset = Invoice.objects.all().order_by('payment_status')

class InvoiceView(FormView):
    template_name = 'barter/invoice_detail.html'
    form_class = InvoiceForm
    model = Invoice

    def post(self, request, *args, **kwargs):
        invoice_form = self.form_class(request.POST)

        if invoice_form.is_valid():
            messages.info(_("Invoice Created"))
            return redirect('barter:invoice-list')
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class AddToCartView(View):
    '''
    Create an order item and add it to the order
    '''
    def session_cart(self, request, offer):
        offer_key = str(offer.pk)
        session_cart = get_or_create_session_cart(request.session)

        if offer_key not in session_cart:
            session_cart[offer_key] = {}
            session_cart[offer_key]['quantity'] = 0

        session_cart[offer_key]['quantity'] += 1

        if not offer.allow_multiple:
            session_cart[offer_key]['quantity'] = 1

        return session_cart

    def post(self, request, *args, **kwargs):
        offer = Offer.on_site.get(slug=self.kwargs["slug"])
        if request.user.is_anonymous:
            request.session['session_cart'] = self.session_cart(request, offer)
        else:
            profile, created = self.request.user.customer_profile.get_or_create(site=get_current_site(request))

            cart = profile.get_cart_or_checkout_cart()

            if cart.status == Invoice.InvoiceStatus.CHECKOUT:
                cart.status = Invoice.InvoiceStatus.CART
                cart.save()

            if profile.has_product(offer.products.all()) and not offer.allow_multiple:
                messages.info(self.request, _("You Have Already Purchased This Item"))
            elif cart.order_items.filter(offer__products__in=offer.products.all()).count() and not offer.allow_multiple:
                messages.info(self.request, _("You already have this product in you cart. You can only buy one"))
            else:
                messages.info(self.request, _("Added item to cart."))
                cart.add_offer(offer)

        return redirect('barter:cart')      # Redirect to cart on success


class RemoveFromCartView(View):
    
    def post(self, request, *args, **kwargs):
        offer = Offer.on_site.get(slug=self.kwargs["slug"])
        if request.user.is_anonymous:
            offer_key = str(offer.pk)
            session_cart = get_or_create_session_cart(request.session)

            if offer_key in session_cart:
                session_cart[offer_key]['quantity'] -= 1

            if session_cart[offer_key]['quantity'] <= 0:
                del(session_cart[offer_key])

            request.session['session_cart'] = session_cart
        else:
            profile = self.request.user.customer_profile.get(site=get_current_site(self.request))      # Make sure they have a cart

            cart = profile.get_cart_or_checkout_cart()

            if cart.status == Invoice.InvoiceStatus.CHECKOUT:
                cart.status = Invoice.InvoiceStatus.CART
                cart.save()

            cart.remove_offer(offer)

        messages.info(self.request, _("Removed item from cart."))

        return redirect('barter:cart')      # Redirect to cart on success


class PaymentSummaryView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'barter/payment_summary.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['payment'] = self.object.payments.filter(success=True).first()
        return context


class OrderHistoryListView(LoginRequiredMixin, ListView):
    '''
    List of all the invoices generated by the current user on the current site.
    '''
    model = Invoice
    # TODO: filter to only include the current user's order history

    def get_queryset(self):
        try:
            # The profile and user are site specific so this should only return what's on the site for that user excluding the cart
            return self.request.user.customer_profile.get(site=get_current_site(self.request)).invoices.filter(status__gt=Invoice.InvoiceStatus.CART)
        except ObjectDoesNotExist:         # Catch the actual error for the exception
            return []   # Return empty list if there is no customer_profile


class OrderHistoryDetailView(LoginRequiredMixin, DetailView):
    '''
    Details of an invoice generated by the current user on the current site.
    '''
    template_name = "barter/invoice_history_detail.html"
    model = Invoice
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'


class ProductsListView(LoginRequiredMixin, ListView):
    model = Receipt
    template_name = 'barter/purchase_list.html'

    def get_queryset(self):
        return self.request.user.customer_profile.get(site=get_current_site(self.request)).receipts.filter(status__gte=PurchaseStatus.COMPLETE)


class ReceiptDetailView(LoginRequiredMixin, DetailView):
    model = Receipt
    template_name = 'barter/purchase_detail.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['payment'] = self.object.order_item.invoice.payments.get(success=True, transaction=self.object.transaction)

        return context

