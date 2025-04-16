from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .firebase import save_user_to_firebase
from firebase_admin import db

@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    save_user_to_firebase(user)

    user_email = user.email
    firebase_users = db.reference("users").get()

    snapshot = db.reference("users").get()

    if isinstance(snapshot, dict):
        for uid, user in snapshot.items():
            if user.get("email") == user_email:
                request.session["user_level"] = user.get("user_level")
                break

    elif isinstance(snapshot, list):
        for idx, user in enumerate(snapshot):
            if isinstance(user, dict) and user.get("email") == user_email:
                request.session["user_level"] = user.get("user_level")
                break



