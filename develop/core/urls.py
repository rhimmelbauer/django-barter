from django.urls import path

from core import views

urlpatterns = [
    path("", views.BarterIndexView.as_view(), name="barter_index"),
    path("product/<slug:slug>/access/", views.ProductAccessView.as_view(), name="product-access"),
    path("account/", views.AccountView.as_view(), name="account"),
]
