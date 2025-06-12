from django.urls import path

from accounts.views import DirectContactBrokerConsultView
from . import views

urlpatterns = [
    path('brokers/', views.BrokerListView.as_view(), name='broker-list'),
    path('<int:pk>/', views.BrokerDetailView.as_view(), name='broker-detail'),
    path('<int:pk>/update/', views.BrokerProfileUpdateView.as_view(), name='broker-update'),
    path('<int:pk>/review/', views.BrokerReviewCreateView.as_view(), name='broker-review'),
    path('<int:pk>/consult/', DirectContactBrokerConsultView.as_view(), name='direct_contact_broker_consult'),
]