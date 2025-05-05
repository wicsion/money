from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_verification_email(request, user):
    verification_link = request.build_absolute_uri(
        f"/accounts/verify-emails/{user.verification_token}/"
    )
    subject = 'Подтверждение emails'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]
    text_content = f'Подтвердите emails по ссылке: {verification_link}'
    html_content = render_to_string('emails/verify_email.html', {
        'verification_link': verification_link
    })

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()