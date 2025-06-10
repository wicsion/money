
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from yookassa import Configuration, Payment
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from yookassa.domain.notification import WebhookNotification
import json
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()
Configuration.account_id = settings.YOOMONEY_ACCOUNT_ID
Configuration.secret_key = settings.YOOMONEY_SECRET_KEY

def payment_topup_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            if amount <= 0:
                messages.error(request, "Сумма должна быть больше 0")
                return redirect('payment_topup')

            payment = Payment.create({
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": request.build_absolute_uri(reverse('payment_success'))
                },
                "capture": True,
                "description": f"Пополнение баланса для {request.user.username}",
                "metadata": {
                    "user_id": request.user.id
                }
            })

            return redirect(payment.confirmation.confirmation_url)

        except Exception as e:
            messages.error(request, f"Ошибка при создании платежа: {str(e)}")
            return redirect('payment_topup')

    return render(request, 'payments/topup.html')

def payment_success_view(request):
    messages.success(request, "Платеж успешно завершен! Баланс будет обновлен в ближайшее время.")
    return redirect('dashboard')


@csrf_exempt
def yookassa_webhook(request):
    logger.info(f"Incoming webhook: {request.body}")
    if request.method == 'POST':
        # Получаем JSON из тела запроса
        event_json = json.loads(request.body)

        try:
            # Проверяем подпись уведомления (важно для безопасности)
            notification = WebhookNotification(event_json)

            # Проверяем, что это уведомление о платеже
            if notification.object.status == 'succeeded':
                payment = notification.object
                metadata = payment.metadata

                if 'user_id' in metadata:
                    user_id = metadata['user_id']
                    amount = float(payment.amount.value)

                    # Находим пользователя и пополняем баланс
                    user = User.objects.get(id=user_id)
                    user.balance += amount
                    user.save()

                    # Можно также создать запись в модели Payment
                    Payment.objects.create(
                        user=user,
                        amount=amount,
                        payment_method='yookassa',
                        status='completed',
                        transaction_id=payment.id
                    )

                    return HttpResponse(status=200)

        except Exception as e:
            # Логируем ошибку
            print(f"Webhook error: {str(e)}")

    return HttpResponse(status=400)