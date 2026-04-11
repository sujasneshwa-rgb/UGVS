from django.core.mail import send_mail
from django.conf import settings

def send_grievance_email(user_email, subject, message):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        fail_silently=False,
    )