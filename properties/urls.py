from django.urls import path
from . import views
from .views import PropertyDeleteView

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property-list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),

    # Новый маршрут для выбора типа (должен быть выше create/)
    path('create/select-type/', views.SelectPropertyTypeView.as_view(), name='select-property-type'),

    # Измененный маршрут с параметром (должен быть выше статических путей)
    path('create/<str:property_type>/', views.PropertyCreateView.as_view(), name='property-create'),

    # Старый маршрут create/ нужно УДАЛИТЬ, так как он конфликтует
    path('<int:pk>/update/', views.PropertyUpdateView.as_view(), name='property-update'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='property-favorite'),
    path('<int:pk>/delete/', PropertyDeleteView.as_view(), name='property-delete'),
    path('api/brokers/', views.BrokerSearchView.as_view(), name='broker-search'),
    path('create/select-listing-type/', views.SelectListingTypeView.as_view(), name='select-listing-type'),


]
