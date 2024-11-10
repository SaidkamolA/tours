from django.conf import settings
from django.core.mail import send_mail

def send_verification_email(email, code):
    send_mail(
        'Подтверждение ',
        f'Ваш проверочный код: {code}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
