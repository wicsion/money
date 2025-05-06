from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ( DetailView,
                                   CreateView,
                                  UpdateView,
                                   DeleteView)
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from django.urls import reverse_lazy
from django.http import JsonResponse
from django_filters.views import FilterView
from .models import Property, PropertyImage, Favorite
from .filters import PropertyFilter
from .forms import PropertyForm, PropertyImageForm


class PropertyListView(FilterView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    filterset_class = PropertyFilter
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            is_approved=True,
            status='active'
        ).select_related('property_type', 'broker', 'developer')


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                property=self.object
            ).exists()
        return context


class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('property-list')  # Или ваш URL

    def get_context_data(self, **kwargs):
        """Добавляем форму для изображений в контекст"""
        context = super().get_context_data(**kwargs)
        context['max_images'] = 10  # Для отображения ограничения в шаблоне
        return context

    def form_valid(self, form):
        """Обработка основной формы и изображений"""
        # Сохраняем объект Property
        self.object = form.save(commit=False)
        self.object.status = 'active'
        self.object.is_premium = False

        # Определяем создателя
        if self.request.user.user_type == 'broker':
            self.object.broker = self.request.user
        elif self.request.user.user_type == 'developer':
            self.object.developer = self.request.user

        self.object.save()

        # Обработка изображений
        images = self.request.FILES.getlist('images')
        if len(images) > 10:
            form.add_error(None, "Максимальное количество фото - 10")
            return self.form_invalid(form)

        for img in images:
            PropertyImage.objects.create(
                property=self.object,
                image=img
            )

        return super().form_valid(form)

    def form_invalid(self, form):
        """Добавляем контекст для отображения ошибок"""
        return self.render_to_response(
            self.get_context_data(form=form, images_error=form.errors)
        )


class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def test_func(self):
        obj = self.get_object()

        return (
            self.request.user == obj.broker or
            self.request.user == obj.developer
        )


    def form_valid(self, form):
        # Сохраняем объект
        self.object = form.save()

        # Обработка новых изображений
        images = self.request.FILES.getlist('images')
        if len(images) + self.object.images.count() > 10:
            form.add_error(None, "Максимальное количество фото - 10")
            return self.form_invalid(form)

        for img in images:
            PropertyImage.objects.create(
                property=self.object,
                image=img
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('property-detail', kwargs={'pk': self.object.pk})


def toggle_favorite(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)

    property = get_object_or_404(Property, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        property=property
    )

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed', 'is_favorite': False})
    return JsonResponse({'status': 'added', 'is_favorite': True})

class BrokerFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        property = get_object_or_404(Property, pk=pk)
        Favorite.objects.get_or_create(
            user=request.user,
            property=property,
            is_broker_favorite=True
        )
        return JsonResponse({'status': 'added'})

class PropertyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Property
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        obj = self.get_object()
        return (
            self.request.user == obj.broker or
            self.request.user == obj.developer
        )