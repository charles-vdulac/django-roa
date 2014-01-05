from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver


@receiver(user_logged_out)
def logged_out_handler(sender, **kwargs):
    """
    User logout signal
    """
    from .backends import reset_api_auth
    reset_api_auth()
