from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from yookassa import Configuration
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from yookassa.domain.notification import WebhookNotification, WebhookNotificationFactory
import json
from django.conf import settings
from django.contrib.auth import get_user_model
import logging
from yookassa import Payment
from payments.models import Payment as PaymentModel

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
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        event_json = json.loads(request.body.decode('utf-8'))

        # Проверка типа события
        if event_json.get('event') != 'payment.succeeded':
            logger.warning(f"Ignored event: {event_json.get('event')}")
            return HttpResponse(status=200)

        # Получение объекта платежа
        payment_object = event_json.get('object', {})
        metadata = payment_object.get('metadata', {})
        payment_id = payment_object.get('id')
        paid = payment_object.get('paid')
        status = payment_object.get('status')

        if status != 'succeeded' or not paid:
            logger.warning(f"Ignored payment: status={status}, paid={paid}")
            return HttpResponse(status=200)

        if 'user_id' not in metadata:
            logger.error("No user_id in metadata")
            return HttpResponse(status=400)

        user_id = metadata['user_id']
        amount = float(payment_object['amount']['value'])

        if PaymentModel.objects.filter(transaction_id=payment_id).exists():
            logger.info(f"Duplicate webhook for payment {payment_id}")
            return HttpResponse(status=200)

        user = User.objects.get(id=user_id)
        user.balance += amount
        user.save()

        PaymentModel.objects.create(
            user=user,
            amount=amount,
            payment_method='yookassa',
            status='completed',
            transaction_id=payment_id
        )

        logger.info(f"User {user_id} balance topped up: {amount} RUB")
        return HttpResponse(status=200)

    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return HttpResponse(status=400)

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return HttpResponse(status=400)
