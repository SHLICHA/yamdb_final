from django.conf import settings
from django.core.mail import send_mail


def mail_send(addres, confirmation_code):
    """Отправка письма с confirmation_code пользователю"""
    send_mail(
        "Пароль от YaMDB",
        f"Ваш пароль: {confirmation_code}",
        settings.DEFAULT_FROM_EMAIL,
        [addres],
        fail_silently=False,
    )
