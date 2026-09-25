from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def send_user_creation_email(sender, instance, created, **kwargs):
    if not created or not instance.email:
        return

    creation_password = getattr(instance, "_creation_password", None)
    mail_text = (
        f"Dear {instance.first_name} {instance.last_name},\n"
        "a new account on EUROMAMMALS website was created for you.\n"
        f"Your username is {instance.username}.\n"
        f"Your password is {creation_password}.\n"
        "Please change your password as soon as possible at this link "
        "https://euromammals.org/accounts/password_change/\n"
        "Kind regards"
    )
    send_mail(
        "Registration to EUROMAMMALS website",
        mail_text,
        None,
        [instance.email],
    )
