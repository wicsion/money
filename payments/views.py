from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View

from .models import Payment
import requests  # Для API платежных систем

from ..accounts.models import ContactRequest, PropertyListing
from ..real_estate_portal import settings


@login_required
def process_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            status='pending'
        )

        # Пример для ЮKassa (Яндекс.Касса)
        response = requests.post(
            'https://api.yookassa.ru/v3/payments',
            auth=('shop_id', 'secret_key'),
            json={
                "amount": {"value": amount, "currency": "RUB"},
                "confirmation": {"type": "redirect", "return_url": "http://your-site.com/payments/callback/"},
                "description": f"Payment #{payment.id}"
            }
        )

        if response.status_code == 200:
            payment.transaction_id = response.json()['id']
            payment.save()
            return redirect(response.json()['confirmation']['confirmation_url'])

    return render(request, 'payments/process.html')


def payment_callback(request):
    payment = Payment.objects.get(transaction_id=request.GET.get('payment_id'))

    if payment.status == 'completed' :
        try:
            subscription = payment.brokersubscription
            subscription.status = 'active'
            subscription.save()

            # Отправка уведомления
            send_mail(
                'Подписка активирована',
                f'Доступ к эксклюзивным объектам {subscription.developer.company} открыт!',
                settings.DEFAULT_FROM_EMAIL,
                [payment.user.email]
            )
        except AttributeError:
            pass

    return render(request, 'payments/callback.html')


class CreatePaymentView(LoginRequiredMixin, View):
    def post(self, request):
        contact_request = get_object_or_404(ContactRequest, pk=request.POST.get('request_id'))

        # Имитация платежа
        payment = Payment.objects.create(
            user=request.user,
            amount=contact_request.payment_amount,
            status='success'
        )

        contact_request.status = 'paid'
        contact_request.transaction_id = payment.id
        contact_request.save()

        return redirect('contact-details', pk=contact_request.pk)


@login_required
def process_listing_payment(request, pk):
    listing = get_object_or_404(PropertyListing, pk=pk)

    # Проверка что пользователь - владелец размещения
    if request.user != listing.broker:
        return HttpResponseForbidden()

    # Расчет стоимости
    amount = 2490 if listing.is_featured else 990

    # Создание платежа
    payment = Payment.objects.create(
        user=request.user,
        amount=amount,
        payment_method='card',
        status='pending'
    )

    # Привязка платежа к размещению
    listing.payment = payment
    listing.save()

    # Интеграция с платежным шлюзом
    # ... ваш код интеграции ...

