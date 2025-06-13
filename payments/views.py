from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from yookassa import Configuration
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from yookassa.domain.notification import WebhookNotification
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
    logger.info(f"Incoming webhook headers: {dict(request.headers)}")
    logger.info(f"Raw webhook body: {request.body.decode('utf-8')}")

    if request.method != 'POST':
        return HttpResponse(status=400)

    try:
        event_json = json.loads(request.body)
        notification = WebhookNotification(event_json)

        # Исправленный вызов (без self)
        if not _verify_signature(request):
            logger.error("Invalid webhook signature")
            return HttpResponse(status=400)

        if notification.object.status == 'succeeded' and notification.object.paid:
            payment = notification.object
            metadata = payment.metadata

            if 'user_id' in metadata:
                user_id = metadata['user_id']
                amount = float(payment.amount.value)

                # Обновляем баланс с дополнительным логированием
                user = User.objects.get(id=user_id)
                logger.info(f"User {user_id} current balance: {user.balance}")
                user.balance += amount
                user.save()
                logger.info(f"User {user_id} new balance: {user.balance}")

                PaymentModel.objects.create(
                    user=user,
                    amount=amount,
                    payment_method='yookassa',
                    status='completed',
                    transaction_id=payment.id
                )

                logger.info(f"Balance updated for user {user_id}: +{amount} RUB")
                return HttpResponse(status=200)
            else:
                logger.error("No user_id in metadata")
        else:
            logger.error(
                f"Payment not succeeded or not paid. Status: {notification.object.status}, Paid: {notification.object.paid}")

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return HttpResponse(status=400)

    return HttpResponse(status=400)


# Перенесите эту функцию ВНЕ yookassa_webhook, но в том же файле
def _verify_signature(request):
    """Проверка подписи вебхука"""
    from hashlib import sha256
    import hmac
    import base64

    secret_key = settings.YOOMONEY_SECRET_KEY.encode('utf-8')
    message = request.body

    # Получаем подпись из заголовка
    signature_header = request.headers.get('X-Content-Signature-SHA256', '')
    if not signature_header:
        logger.error("Missing X-Content-Signature-SHA256 header")
        return False

    try:
        signature = signature_header.split('=')[1]
    except IndexError:
        logger.error(f"Malformed signature header: {signature_header}")
        return False

    # Вычисляем HMAC
    hmac_obj = hmac.new(secret_key, message, sha256)
    calculated_signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')

    logger.info(f"Calculated signature: {calculated_signature}")
    logger.info(f"Received signature: {signature}")

    return hmac.compare_digest(calculated_signature, signature)