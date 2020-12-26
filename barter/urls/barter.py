from django.urls import path

from barter.views import barter as barter_views

app_name = "barter"

urlpatterns = [
    path('cart/', barter_views.CartView.as_view(), name="cart"),
    path('cart/add/<slug:slug>/', barter_views.AddToCartView.as_view(), name="add-to-cart"),
    path('cart/remove/<slug:slug>/', barter_views.RemoveFromCartView.as_view(), name="remove-from-cart"),
    path('checkout/summary/<uuid:uuid>/', barter_views.PaymentSummaryView.as_view(), name="purchase-summary"),

    # path('cart/remove/<slug:slug>/', barter_views.TransactionSummary.as_view(), name="transaction-summary"),
    # path('cart-item/edit/<int:id>/', barter_views.CartItemQuantityEditView.as_view(), name='barter-cart-item-quantity-edit'),
    # path('retrieve/cart/', barter_views.RetrieveCartView.as_view(), name='barter-user-cart-retrieve'),
    # path('delete/cart/<int:id>/', barter_views.DeleteCartView.as_view(), name='barter-user-cart-delete'),
    # path('retrieve/order/<int:id>/', barter_views.RetrieveOrderView.as_view(), name='barter-user-order-retrieve'),
    # path('retrieve/purchase-item/<int:id>/', barter_views.RetrievePurchaseView.as_view(), name='barter-user-purchase-retrieve'),
    # path('retrieve/purchase/list/', barter_views.RetrievePurchaseListView.as_view(), name='barter-user-purchase-list'),
    # path('retrieve/order-summary/', barter_views.RetrieveOrderSummaryView.as_view(), name='barter-order-summary-retrieve'),
    # path('payment/processing/', barter_views.PaymentProcessingView.as_view(), name='barter-payment-processing'),
    # path('request/refund/<int:id>/', barter_views.RequestRefundView.as_view(), name='barter-request-refund'),
    # path('retrieve/refund/requests/', barter_views.RetrieveRefundRequestsView.as_view(), name='barter-retrieve-refund-requests'),
    # path('issue/refund/<int:id>/', barter_views.IssueRefundView.as_view(), name='barter-issue-refund'),
    
    path('checkout/account/', barter_views.AccountInformationView.as_view(), name="checkout-account"),
    path('checkout/payment/', barter_views.PaymentView.as_view(), name="checkout-payment"),
    path('checkout/review/', barter_views.ReviewCheckoutView.as_view(), name="checkout-review"),

    path('customer/products/', barter_views.ProductsListView.as_view(), name="customer-products"),
    path('customer/product/<uuid:uuid>/receipt/', barter_views.ReceiptDetailView.as_view(), name="customer-receipt"),
    path('customer/subscriptions/', barter_views.SubscriptionsListView.as_view(), name="customer-subscriptions"),
    path('customer/subscription/<uuid:uuid>/cancel/', barter_views.SubscriptionCancelView.as_view(), name="customer-subscription-cancel"),
    path('customer/subscription/update/<uuid:uuid>/payment', barter_views.SubscriptionUpdatePaymentView.as_view(), name="customer-subscription-update-payment"),
    path('customer/shipping/<int:pk>/update', barter_views.ShippingAddressUpdateView.as_view(), name="customer-shipping-update"),               # TODO: [GK-3030] Do not use PKs in URLs

    # TODO: Add user's account mangement urls
    # TODO: add user's order details page
]
