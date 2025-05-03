from django.core.mail import send_mail
from django.conf import settings

def send_notification(user, subject, message):
    """
    Отправляет уведомление пользователю (по электронной почте, если настроено)
    
    Args:
        user: Пользователь Django, которому нужно отправить уведомление
        subject: Тема уведомления
        message: Текст уведомления
    """
    # Проверка, есть ли у пользователя электронная почта
    if user.email:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@lostandfound.com',
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email notification: {str(e)}")
    
    # Здесь можно добавить другие способы уведомления (например, SMS, push-уведомления)
    # в зависимости от требований проекта