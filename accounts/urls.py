from django.urls import path


from . import views
from .views import (
    RegisterView,
    verify_email,
    EmailVerificationSentView,
    BrokerProfileUpdateView,
    SubscriptionView,
    dashboard_view,
    invalid_token_view,
    login_view,
    logout_view,
    CompleteRegistrationView,
    PropertyCreateView,
    ToggleFavoriteView,
    ContactRequestView,
    ContactRequestDetailView,
    MessageCreateView,
    UpdateRequestStatusView,
    SubscriptionManagementView,
    SubscriptionDeleteView,
    ListingCreateView,
    PropertyDeleteView,

)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/update/', BrokerProfileUpdateView.as_view(), name='profile-update'),
    path('subscriptions/', SubscriptionView.as_view(), name='subscriptions'),
    path('verify-email/<str:token>/', verify_email, name='verify_email'),
    path('invalid-token/', invalid_token_view, name='invalid_token'),
    path('email-verification-sent/', EmailVerificationSentView.as_view(), name='email_verification_sent'),
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete_registration'),
    path('property/create/', PropertyCreateView.as_view(), name='create_property'),
    path('toggle-favorite/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('broker/<int:pk>/contact/', ContactRequestView.as_view(), name='contact_broker'),
    path('contact-request/new/', ContactRequestView.as_view(), name='new_contact_request'),
    path('contact-request/<int:pk>/', ContactRequestDetailView.as_view(), name='contact_request_detail'),
    path('contact-request/<int:pk>/status/<str:status>/', UpdateRequestStatusView.as_view(),name='update_request_status'),
    path('ajax/load-properties/', views.load_properties, name='load_properties'),
    path('subscribe/<int:developer_id>/', views.SubscribeView.as_view(), name='subscribe'),
    path('exclusive-properties/', views.ExclusivePropertiesView.as_view(), name='exclusive_properties'),
    path('developers/', views.DevelopersListView.as_view(), name='developers_list'),
    path('subscriptions/manage/', SubscriptionManagementView.as_view(), name='subscription_management'),
    path('listing/create/', ListingCreateView.as_view(), name='create_listing'),
    path('subscription/delete/<int:pk>/', SubscriptionDeleteView.as_view(), name='delete_subscription'),
    path('api/chat/<int:pk>/', views.ChatAPIView.as_view(), name='chat-api'),
    path('api/typing/<int:pk>/', views.TypingAPIView.as_view(), name='typing-api'),
    path('contact-request/<int:pk>/message/', MessageCreateView.as_view(), name='add_message'),
    path('properties/<int:pk>/delete/', PropertyDeleteView.as_view(), name='property-delete'),
]
