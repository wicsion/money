from django.db.models import Q
from django.views.generic import DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import  UpdateView, ListView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.http import JsonResponse, HttpResponseForbidden
from django.views import View
from django.contrib import messages
from .models import  StatusLog
import random
import string
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.exceptions import PermissionDenied
from .models import (User, UserActivity,
                     Subscription,
                     Favorite,
                     ContactRequest,
                     Message,
                     DeveloperProfile,
                     BrokerSubscription,
                     ExclusiveProperty, PropertyListing)

from .forms import (UserRegistrationForm, RoleSelectionForm,
                    ProfileForm, ContactRequestForm, BrokerProfileForm)

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from properties.forms import PropertyForm
from payments.models import Payment
from properties.models import Property
from brokers.forms import BrokerReviewForm

from brokers.models import BrokerProfile,BrokerReview


def home_view(request):
    return render(request, 'home.html')


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('email_verification_sent')

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.is_active = False
            user.verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
            # Начисляем 100 рублей на основной баланс
            user.balance = 100.00  # Или user.balance += 100.00, если хотим добавлять к существующему
            user.save()
            self.send_verification_email(user)
            return redirect(self.success_url)
        except Exception as e:
            form.add_error(None, f"Ошибка: {str(e)}")
            return self.form_invalid(form)

    def send_verification_email(self, user):
        verification_link = self.request.build_absolute_uri(
            f"/accounts/verify-email/{user.verification_token}/"
        )
        subject = 'Подтверждение email'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]
        html_content = render_to_string('emails/verify_email.html', {
            'verification_link': verification_link,
            'user': user
        })
        msg = EmailMultiAlternatives(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()


class CompleteRegistrationView(LoginRequiredMixin, View):
    template_name = 'accounts/complete-registration.html'

    def get(self, request):
        role_form = RoleSelectionForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user)
        return render(request, self.template_name, {
            'role_form': role_form,
            'profile_form': profile_form
        })

    def post(self, request):
        role_form = RoleSelectionForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if role_form.is_valid() and profile_form.is_valid():
            user = role_form.save(commit=False)
            user.user_type = role_form.cleaned_data['role']
            profile_form.save()

            user.is_verified = True
            user.is_active = True
            user.save()

            if user.user_type == User.UserType.BROKER:
                return redirect('complete_broker_info')
            return redirect('dashboard')

        else:

            import logging
            logger = logging.getLogger('django')
            logger.error("Role form errors: %s", role_form.errors.as_json())
            logger.error("Profile form errors: %s", profile_form.errors.as_json())

        return render(request, self.template_name, {
            'role_form': role_form,
            'profile_form': profile_form
        })


class EmailVerificationSentView(TemplateView):
    template_name = 'accounts/email_verification_sent.html'


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            UserActivity.objects.create(user=user, action="Вход в систему")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        UserActivity.objects.create(user=request.user, action="Выход из системы")
    logout(request)
    return redirect('home')


class BrokerProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user


class SubscriptionView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'accounts/subscriptions.html'

    def get_queryset(self):
        return self.request.user.subscriptions.filter(is_active=True)


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    active_tab = request.GET.get('tab', 'properties')
    user = request.user
    context = {'active_tab': active_tab}

    # Общие данные
    context.update({
        'activities': UserActivity.objects.filter(user=user).order_by('-timestamp')[:10],
        'contact_requests': user.accounts_received_requests.all() if user.is_broker else []
    })

    # Данные по ролям
    if user.user_type == User.UserType.BROKER:
        context.update({
            'my_properties': Property.objects.filter(broker=user.broker_profile) if hasattr(user, 'broker_profile') else [],
            'all_requests': user.accounts_received_requests.all().order_by('-created_at'),
            'active_requests_count': user.accounts_received_requests.filter(status='in_progress').count()
        })
    elif user.user_type == User.UserType.DEVELOPER:
        context['developer_properties'] = user.created_properties.filter(is_approved=True)
    elif user.user_type == User.UserType.CLIENT:
        if active_tab == 'properties':
            context['favorite_properties'] = Favorite.objects.filter(
                user=request.user,
                favorite_type='client'
            ).select_related('property')
        else:
            context['broker_favorites'] = Favorite.objects.filter(
                user=request.user,
                favorite_type='broker'
            ).select_related('broker')

    if user.is_broker:
        context.update({
            'active_listings': user.listings.filter(is_active=True),
            'expired_listings': user.listings.filter(is_active=False)
        })

    return render(request, 'accounts/dashboard.html', context)

def invalid_token_view(request):
    return render(request, 'accounts/invalid_token.html')


class RoleSelectionView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/role_selection.html'
    form_class = RoleSelectionForm
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_verified = True
        user.save()
        return super().form_valid(form)


def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.is_active = True
        user.verification_token = ''
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('complete_registration')
    except User.DoesNotExist:
        return redirect('invalid_token')


class PropertyCreateView(LoginRequiredMixin, CreateView):
    form_class = PropertyForm
    template_name = 'accounts/property_create.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Проверяем наличие профиля брокера
        if not hasattr(self.request.user, 'broker_profile'):
            messages.error(self.request, "Профиль брокера не найден")
            return redirect('complete_broker_profile')  # Перенаправление на заполнение профиля

        form.instance.creator = self.request.user
        form.instance.broker = self.request.user.broker_profile  # Используем профиль брокера
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard')


# views.py (исправленная версия)
class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request):
        obj_type = request.POST.get('type')
        obj_id = request.POST.get('id')
        redirect_url = request.POST.get('next', '/')

        try:
            if obj_type == 'property':
                obj = get_object_or_404(Property, id=obj_id)
                favorite, created = Favorite.objects.get_or_create(
                    user=request.user,
                    property=obj,
                    favorite_type='client'
                )
            elif obj_type == 'broker':
                broker_user = get_object_or_404(User, id=obj_id, user_type=User.UserType.BROKER)
                favorite, created = Favorite.objects.get_or_create(
                    user=request.user,
                    broker=broker_user,
                    favorite_type='broker'
                )
            else:
                messages.error(request, "Неверный тип объекта")
                return redirect(redirect_url)

            if not created:
                favorite.delete()
                messages.success(request, "Успешно удалено из избранного")
            else:
                messages.success(request, "Успешно добавлено в избранное")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'action': 'removed' if not created else 'added'
                })

            return redirect(redirect_url)

        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")
            return redirect(redirect_url)

def load_properties(request):
    broker_id = request.GET.get('broker_id')
    properties = Property.objects.filter(creator_id=broker_id)
    return render(request, 'accounts/property_dropdown.html', {'properties': properties})


class ContactRequestDetailView(LoginRequiredMixin, DetailView):
    model = ContactRequest
    template_name = 'accounts/contact_request_detail.html'
    paginate_by = 50


    def get(self, request, *args, **kwargs):
        print("ContactRequestDetailView called!")  # Добавьте эту строку
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            Q(requester=self.request.user) |
            Q(broker=self.request.user)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = self.object.messages.all().order_by('created_at')
        context['has_review'] = BrokerReview.objects.filter(
            contact_request=self.object,
            client=self.object.requester
        ).exists()
        return context


class ContactRequestView(LoginRequiredMixin, CreateView):
    model = ContactRequest
    form_class = ContactRequestForm
    template_name = 'accounts/contact_request_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.requester = self.request.user
        response = super().form_valid(form)

        # Генерируем абсолютную ссылку на запрос
        request_url = self.request.build_absolute_uri(
            reverse('contact_request_detail', kwargs={'pk': self.object.pk})
        )

        if settings.EMAIL_HOST_USER:
            subject = f'Новый запрос от {self.request.user.get_full_name()}'
            html_message = render_to_string('emails/new_request_email.html', {
                'contact_request': self.object,
                'request_url': request_url,  # Теперь переменная определена
                'broker': self.object.broker
            })
            send_mail(
                subject,
                '',  # Пустое текстовое сообщение
                settings.DEFAULT_FROM_EMAIL,
                [self.object.broker.email],
                html_message=html_message  # Передаем HTML-контент
            )

        return response

    def get_success_url(self):
        return reverse('contact_request_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_client:
            raise PermissionDenied("Только клиенты могут отправлять запросы")
        return super().dispatch(request, *args, **kwargs)



class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['text', 'attachment']  # Объединенная версия с вложениями

    def form_valid(self, form):
        contact_request = get_object_or_404(ContactRequest, pk=self.kwargs['pk'])
        form.instance.contact_request = contact_request
        form.instance.sender = self.request.user
        self.object = form.save()  # Сохраняем объект перед рендерингом
        return render(self.request, 'accounts/partials/message.html', {'message': self.object})


    def form_invalid(self, form):
        return JsonResponse({'errors': form.errors}, status=400)

    def dispatch(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return super().dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


class UpdateRequestStatusView(LoginRequiredMixin, View):
    def post(self, request, pk, status):
        contact_request = get_object_or_404(ContactRequest, pk=pk, broker=request.user)
        previous_status = contact_request.status
        contact_request.status = status
        contact_request.save()

        # Создаем запись в истории статусов
        StatusLog.objects.create(
            contact_request=contact_request,
            status=status,
            changed_by=request.user
        )
        return redirect('contact_request_detail', pk=pk)


class SubscribeView(LoginRequiredMixin, View):
    def get(self, request, developer_id):
        developer = get_object_or_404(DeveloperProfile, id=developer_id)
        return render(request, 'accounts/subscribe.html', {
            'developer': developer,
            'user': request.user
        })

    def post(self, request, developer_id):
        developer = get_object_or_404(DeveloperProfile, id=developer_id)
        subscription_type = request.POST.get('subscription_type')

        # Расчет стоимости
        price_map = {
            '1_month': 990,
            '3_months': 2490,
            '6_months': 4490
        }

        # Создание платежа
        payment = Payment.objects.create(
            user=request.user,
            amount=price_map[subscription_type],
            payment_method='card',
            status='pending'
        )

        # Создание подписки
        subscription = BrokerSubscription.objects.create(
            broker=request.user,
            developer=developer,
            end_date=timezone.now() + relativedelta(months=int(subscription_type[0])),
            payment=payment
        )

        return redirect('process_payment', payment_id=payment.id)


class ExclusivePropertiesView(LoginRequiredMixin, ListView):
    template_name = 'accounts/exclusive_properties.html'  # ← Добавьте эту строку
    context_object_name = 'properties'

    def get_queryset(self):
        return ExclusiveProperty.objects.filter(
            developer__in=self.request.user.broker_subscriptions.filter(
                status='active',
                end_date__gte=timezone.now()
            ).values('developer'),
            subscription_required=True
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_broker:
            raise PermissionDenied("Доступно только для брокеров")
        return super().dispatch(request, *args, **kwargs)

class DevelopersListView(LoginRequiredMixin, ListView):
    model = DeveloperProfile
    template_name = 'accounts/exclusive_properties.html'
    context_object_name = 'developers'

    def get_queryset(self):
        return DeveloperProfile.objects.filter(is_verified=True)


class SubscriptionManagementView(LoginRequiredMixin, View):
    template_name = 'accounts/subscription_management.html'

    def get(self, request):
        subscriptions = request.user.broker_subscriptions.all()
        return render(request, self.template_name, {'subscriptions': subscriptions})


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = PropertyListing
    fields = ['property', 'end_date', 'is_featured']
    template_name = 'accounts/create_listing.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['property'].queryset = Property.objects.filter(creator=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.broker = self.request.user
        # Автоматическая установка is_active
        form.instance.is_active = True if form.instance.end_date > timezone.now() else False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('process_listing_payment', kwargs={'pk': self.object.pk})


class SubscriptionDeleteView(LoginRequiredMixin, DeleteView):
    model = BrokerSubscription
    success_url = reverse_lazy('subscription_management')


class ChatAPIView(View):
    def get(self, request, pk):
        try:
            contact_request = ContactRequest.objects.get(pk=pk)
            if request.user not in [contact_request.requester, contact_request.broker]:
                return JsonResponse({'error': 'Forbidden'}, status=403)

            messages = contact_request.messages.all().values(
                'id',
                'text',
                'created_at',
                'sender__id',
                'sender__first_name',
                'attachment'
            )
            return JsonResponse(list(messages), safe=False)

        except ContactRequest.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)


class TypingAPIView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

    def post(self, request, pk):
        try:
            contact_request = ContactRequest.objects.get(pk=pk)
            # Сохраняем время последней активности
            request.user.last_activity = timezone.now()
            request.user.save()
            return JsonResponse({'status': 'typing'})
        except ContactRequest.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Property
    fields = ['title', 'description', 'price']
    template_name = 'accounts/property_create.html'
    success_url = reverse_lazy('dashboard')

    # Проверка прав
    def test_func(self):
        return self.request.user == self.get_object().creator  # Используем creator вместо user

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

class PropertyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Property
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        return self.request.user == self.get_object().creator



class CreateRequestChoiceView(LoginRequiredMixin, View):
    template_name = 'accounts/create_request_choice.html'

    def get(self, request):
        if not request.user.is_client:
            raise PermissionDenied("Доступно только для клиентов")
        return render(request, self.template_name)


class BrokerListView(ListView):
    model = User
    template_name = 'accounts/broker_list.html'
    context_object_name = 'brokers'

    def get_queryset(self):
        return BrokerProfile.objects.filter(user__is_verified=True)


class DeveloperListView(ListView):
    model = DeveloperProfile
    template_name = 'accounts/developer_list.html'
    context_object_name = 'developers'


class DirectContactBrokerView(LoginRequiredMixin, View):
    def get(self, request, pk, property_id):
        # Проверяем тип пользователя через user_type
        if request.user.user_type != User.UserType.CLIENT:
            messages.error(request, "Только клиенты могут отправлять запросы")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Получаем брокера и связанный объект Property
        broker_user = get_object_or_404(
            User,
            pk=pk,
            user_type=User.UserType.BROKER
        )
        broker_profile = get_object_or_404(
            BrokerProfile,
            user=broker_user
        )
        property_obj = get_object_or_404(
            Property,
            pk=property_id,
            broker=broker_profile
        )

        # Создаем или получаем запрос
        contact_request, created = ContactRequest.objects.get_or_create(
            requester=request.user,
            broker=broker_user,
            property=property_obj,
            defaults={'status': 'new'}
        )

        return redirect('contact_request_detail', pk=contact_request.pk)


def delete_request(request, pk):
    if request.method == 'POST':
        # Ищем запрос, где пользователь является requester или broker
        req = get_object_or_404(
            ContactRequest,
            Q(pk=pk) & (Q(requester=request.user) | Q(broker=request.user))
        )
        req.delete()
        messages.success(request, "Запрос успешно удален")
    return redirect('dashboard')

class CompleteBrokerInfoView(LoginRequiredMixin, UpdateView):
    form_class =  BrokerProfileForm
    template_name = 'accounts/complete_broker_info.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        # Создаем или получаем профиль брокера
        broker_profile, created = BrokerProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'license_number': '',
                'experience': 0,
                'about': ''
            }
        )
        return broker_profile

    def form_valid(self, form):
        broker_profile = form.save(commit=False)
        broker_profile.user = self.request.user
        broker_profile.save()

        # Принудительно обновляем is_profile_complete
        user = self.request.user
        user.is_verified = True
        user.save()  # Вызовет пересчёт is_profile_complete через модель User

        return redirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['experience'].required = True
        form.fields['license_number'].required = True
        return form

    def get_queryset(self):
        # Фильтруем подтвержденные профили брокеров
        return BrokerProfile.objects.filter(
            user__is_verified=True,
            user__user_type=User.UserType.BROKER,
            is_approved=True  # Если требуется модерация
        )


class DirectContactBrokerConsultView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if request.user.user_type != User.UserType.CLIENT:
            messages.error(request, "Только клиенты могут отправлять запросы")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        broker = get_object_or_404(User, pk=pk, user_type=User.UserType.BROKER)

        # Создаем запрос с явным указанием property=None
        contact_request, created = ContactRequest.objects.get_or_create(
            requester=request.user,
            broker=broker,
            defaults={
                'status': 'new',
                'property': None  # Явное указание на консультацию
            }
        )

        return redirect('contact_request_detail', pk=contact_request.pk)

class SubmitReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        contact_request = get_object_or_404(ContactRequest, pk=pk)
        broker_profile = contact_request.broker.broker_profile

        # Проверка условий
        if not (
            contact_request.status == 'completed'
            and request.user == contact_request.requester
            and not BrokerReview.objects.filter(contact_request=contact_request).exists()
        ):
            return HttpResponseForbidden("Недостаточно прав для отправки отзыва")

        # Обработка формы
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            messages.error(request, "Заполните все поля")
            return redirect('contact_request_detail', pk=pk)

        try:
            # Создаем отзыв
            review = BrokerReview.objects.create(
                broker=broker_profile,
                client=request.user,
                contact_request=contact_request,
                rating=rating,
                comment=comment,
                is_approved=True  # Если требуется модерация - установите False
            )
            broker_profile.update_rating()
            messages.success(request, "Отзыв успешно отправлен!")
        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")

        return redirect('contact_request_detail', pk=pk)

