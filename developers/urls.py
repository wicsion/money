from django.urls import path
from . import views

urlpatterns = [
    path('', views.DeveloperListView.as_view(), name='developer-list'),
    path('<int:pk>/', views.DeveloperDetailView.as_view(), name='developer-detail'),
    path('<int:pk>/update/', views.DeveloperProfileUpdateView.as_view(), name='developer-update'),
]