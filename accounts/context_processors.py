from django.utils import timezone
from .models import BrokerSubscription
from payments.models import Payment


def subscriptions(request):
    if request.user.is_authenticated and request.user.is_broker:
        return {
            'active_subscriptions': BrokerSubscription.objects.filter(
                broker=request.user,
                status='active',
                end_date__gte=timezone.now()
            ).select_related('developer')
        }
    return {}

def payment_info(request):
    if request.user.is_authenticated and request.user.is_broker:
        return {
            'pending_payments': Payment.objects.filter(
                user=request.user,
                status='pending'
            )
        }
    return {}