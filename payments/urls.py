from django.urls import path
from . import views

urlpatterns = [
    path('process/', views.process_payment, name='process_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('process/listing/<int:pk>/', views.process_listing_payment, name='process_listing_payment'),
]