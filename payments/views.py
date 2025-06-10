from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from yookassa import Configuration, Payment
from django.conf import settings


# Настройка должна быть глобальной (один раз при запуске приложения)
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