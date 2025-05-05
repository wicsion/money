from django.urls import path
from . import views
from .views import PropertyUpdateView, PropertyDeleteView

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property-list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),
    path('create/', views.PropertyCreateView.as_view(), name='property-create'),
    path('<int:pk>/update/', views.PropertyUpdateView.as_view(), name='property-update'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='property-favorite'),
    path('<int:pk>/update/', PropertyUpdateView.as_view(), name='property-update'),
    path('<int:pk>/delete/', PropertyDeleteView.as_view(), name='property-delete'),
]