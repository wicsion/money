from django.db import transaction
from django.db.models import Q
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
from .models import Property, PropertyImage,  PropertyType
from .filters import PropertyFilter
from .forms import PropertyForm
from  accounts.models import User
from accounts.models import Favorite
from django.contrib.auth.decorators import login_required

class PropertyListView(FilterView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    filterset_class = PropertyFilter
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        broker_id = self.request.GET.get('broker')
        if broker_id:
            queryset = queryset.filter(broker_id=broker_id)
        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            properties = self.get_queryset()
            data = {
                'options': ''.join([f'<option value="{p.id}">{p.title}</option>' for p in properties])
            }
            return JsonResponse(data)
        return super().render_to_response(context, **response_kwargs)


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
    template_name = 'properties/property_create_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        """Добавляем форму для изображений в контекст"""
        context = super().get_context_data(**kwargs)
        context['max_images'] = 10  # Для отображения ограничения в шаблоне
        property_type = get_object_or_404(PropertyType, name=self.kwargs['property_type'])
        context['property_type_name'] = property_type.get_name_display()
        context['show_apartment_fields'] = property_type.name in ['new_flat', 'resale_flat']
        context['step'] = 1
        return context

    def form_valid(self, form):
        with transaction.atomic():  # Начало атомарной транзакции
            # Проверка наличия профиля брокера
            if not hasattr(self.request.user, 'broker_profile'):
                form.add_error(None, "Профиль брокера не найден. Заполните данные в разделе профиля.")
                return self.form_invalid(form)

            # Проверка главного изображения
            if 'main_image' not in self.request.FILES:
                form.add_error('main_image', 'Главное изображение обязательно')
                return self.form_invalid(form)

            # Получение списка изображений
            images = self.request.FILES.getlist('images')

            # Проверка лимита изображений (10 максимум)
            if len(images) > 10:
                form.add_error(None, "Максимальное количество изображений - 10")
                return self.form_invalid(form)

            # Установка обязательных полей
            form.instance.property_type = get_object_or_404(
                PropertyType,
                name=self.kwargs['property_type']
            )
            form.instance.broker = self.request.user.broker_profile
            form.instance.is_approved = False
            form.instance.creator = self.request.user  # Если нужно сохранить создателя

            # Сохранение объекта Property
            self.object = form.save()

            # Привязка изображений к объекту
            main_image = self.request.FILES['main_image']
            PropertyImage.objects.create(
                property=self.object,
                image=main_image,
                is_main=True
            )

            # Сохранение дополнительных изображений
            for idx, img in enumerate(images[:9], start=1):  # 9 + 1 main = 10
                PropertyImage.objects.create(
                    property=self.object,
                    image=img,
                    order=idx
                )

            return super().form_valid(form)



    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['property_type'] = get_object_or_404(
            PropertyType,
            name=self.kwargs['property_type']
        )
        return kwargs


    def form_invalid(self, form):
     """Добавляем контекст для отображения ошибок"""
     return self.render_to_response(
        self.get_context_data(form=form, images_error=form.errors)
    )


class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_create_form.html'

    def test_func(self):
        obj = self.get_object()
        # Проверяем владельца-брокера через связь BrokerProfile.user
        is_broker_owner = (
                obj.broker and
                self.request.user == obj.broker.user
        )
        # Проверяем владельца-застройщика
        is_developer_owner = self.request.user == obj.developer
        return is_broker_owner or is_developer_owner


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

@login_required
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
        # Проверяем связь через BrokerProfile.user
        is_broker_owner = (
                obj.broker and
                self.request.user == obj.broker.user
        )
        is_developer_owner = self.request.user == obj.developer
        return is_broker_owner or is_developer_owner

class SelectPropertyTypeView(LoginRequiredMixin, View):
    template_name = 'properties/select_property_type.html'

    def get(self, request):
        return render(request, self.template_name, {
            'types': PropertyType.objects.all()

        })


class BrokerSearchView(View):
    def get(self, request):
        search = request.GET.get('search', '')
        brokers = User.objects.filter(
            user_type=User.UserType.BROKER  # Используем правильный фильтр по типу
        ).filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(patronymic__icontains=search)
        )[:10]

        brokers_data = [{
            "id": broker.id,
            "name": broker.get_full_name(),  # Полное ФИО
            "avatar": broker.avatar.url if broker.avatar else "/static/default_avatar.png"
        } for broker in brokers]

        return JsonResponse({"brokers": brokers_data})