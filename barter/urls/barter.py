from django.urls import path

from barter.views import barter as barter_views

app_name = "barter"

urlpatterns = [
    path('orders/', barter_views.InvoiceListView.as_view(), name="invoice-list"),
    # path('order/', barter_views.CartView.as_view(), name="cart"),
    # path('orders/add/<slug:slug>/', barter_views.AddToCartView.as_view(), name="add-to-cart"),
    # path('orders/remove/<slug:slug>/', barter_views.RemoveFromCartView.as_view(), name="remove-from-cart"),
    # path('order/summary/<uuid:uuid>/', barter_views.PaymentSummaryView.as_view(), name="purchase-summary"),
    # path('order/fulfillment/<uuid:uuid>/', barter_views.PaymentSummaryView.as_view(), name="purchase-summary"),
    
    # path('paymets/', barter_views.AccountInformationView.as_view(), name="checkout-account"),
    # path('payment/', barter_views.PaymentView.as_view(), name="checkout-payment"),
    # path('payment/<uuid:uuid>', barter_views.ReviewCheckoutView.as_view(), name="checkout-review"),

    # path('customer/products/', barter_views.ProductsListView.as_view(), name="customer-products"),
    # path('customer/product/<uuid:uuid>/receipt/', barter_views.ReceiptDetailView.as_view(), name="customer-receipt"),
    # path('customer/subscriptions/', barter_views.SubscriptionsListView.as_view(), name="customer-subscriptions"),
    # path('customer/subscription/<uuid:uuid>/cancel/', barter_views.SubscriptionCancelView.as_view(), name="customer-subscription-cancel"),
    # path('customer/subscription/update/<uuid:uuid>/payment', barter_views.SubscriptionUpdatePaymentView.as_view(), name="customer-subscription-update-payment"),
    # path('customer/shipping/<int:pk>/update', barter_views.ShippingAddressUpdateView.as_view(), name="customer-shipping-update"),               # TODO: [GK-3030] Do not use PKs in URLs

    
]
