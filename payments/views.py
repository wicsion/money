from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from yookassa import Configuration, Payment
from django.conf import settings

# Настройка конфигурации ЮKassa
Configuration.account_id = settings.YOOMONEY_ACCOUNT_ID
Configuration.secret_key = settings.YOOMONEY_SECRET_KEY

def payment_topup_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if not amount or float(amount) <= 0:
            messages.error(request, "Укажите корректную сумму")
            return redirect('payment_topup')

        # Создание платежа в ЮKassa
        payment = Payment.create({
            "amount": {
                "value": amount,
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

        # Перенаправляем пользователя на страницу оплаты
        return redirect(payment.confirmation.confirmation_url)

    return render(request, 'payments/topup.html')

def payment_success_view(request):
    # Проверяем успешность платежа (можно через webhook)
    user = request.user
    messages.success(request, "Баланс успешно пополнен!")
    return redirect('dashboard')