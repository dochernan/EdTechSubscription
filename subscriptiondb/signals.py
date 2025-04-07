from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .firebase import save_user_to_firebase

@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    save_user_to_firebase(user)

