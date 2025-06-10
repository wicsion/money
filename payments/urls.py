from django.urls import path
from.views import payment_topup_view, payment_success_view


urlpatterns = [
    path('payment/topup/', payment_topup_view, name='payment_topup'),
    path('payment/success/', payment_success_view, name='payment_success'),
]
