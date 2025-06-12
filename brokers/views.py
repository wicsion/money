from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import BrokerProfile, BrokerReview, ContactRequest
from properties.forms import PropertyForm
from accounts.models import Subscription, Favorite, User
from properties.models import Property
from .forms import BrokerProfileForm, BrokerReviewForm
from django.utils import timezone
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View



class BrokerPropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'brokers/property_list.html'
    context_object_name = 'properties'

    def get_queryset(self):
        return Property.objects.filter(broker=self.request.user)


class PropertyCreateWithSubscriptionCheck(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_create_form.html'

    def form_valid(self, form):
        if self.request.user.user_type == 'broker':
            active_sub = Subscription.objects.filter(
                user=self.request.user,
                end_date__gte=timezone.now().date()
            ).exists()

            if not active_sub and form.cleaned_data.get('is_premium'):
                return HttpResponseForbidden("Требуется активная подписка для премиум-объявлений")

        form.instance.user = self.request.user
        return super().form_valid(form)


class BrokerListView(ListView):
    model = BrokerProfile
    template_name = 'brokers/broker_list.html'
    context_object_name = 'brokers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')

        if search_query:
            # Ищем по полному имени пользователя (first_name + last_name)
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__patronymic__icontains=search_query)
            )

        return queryset.filter(is_archived=False, is_approved=True)


class BrokerDetailView(DetailView):
    model = BrokerProfile
    template_name = 'brokers/broker_detail.html'
    context_object_name = 'broker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        context['broker_properties'] = Property.objects.filter(
            broker=self.object,
            status='active',
            is_approved=True
        )[:4]

        # Проверка избранного
        is_favorite = False
        user = self.request.user
        if user.is_authenticated:
            is_favorite = Favorite.objects.filter(
                user=user,
                broker=self.object.user,
                favorite_type='broker'
            ).exists()

        context['is_favorite'] = is_favorite
        return context


class BrokerProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BrokerProfile
    form_class = BrokerProfileForm
    template_name = 'brokers/broker_update.html'

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        return reverse_lazy('broker-detail', kwargs={'pk': self.object.pk})


class BrokerReviewCreateView(LoginRequiredMixin, CreateView):
    model = BrokerReview
    form_class = BrokerReviewForm
    template_name = 'brokers/review_create.html'

    def form_valid(self, form):
        form.instance.broker = get_object_or_404(BrokerProfile, pk=self.kwargs['pk'])
        form.instance.client = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('broker-detail', kwargs={'pk': self.kwargs['pk']})


class BrokerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'brokers/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        broker = self.request.user.broker_profile

        from real_estate_portal.accounts.models import Favorite
        context.update({
            'my_properties': Property.objects.filter(broker=self.request.user),
            'contact_requests': ContactRequest.objects.filter(broker=self.request.user),
            'favorites': Favorite.objects.filter(property__broker=self.request.user),
            'subscriptions': Subscription.objects.filter(user=self.request.user)
        })
        return context


