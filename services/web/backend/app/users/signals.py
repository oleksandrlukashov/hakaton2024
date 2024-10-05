from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, TwoFactorAuthentication

@receiver(post_save, sender=User)
def create_or_update_2fa(sender, instance, created, **kwargs):
    """Create or update the 2FA setup for a new user."""
    if created:
        instance.twofactorauthentication = TwoFactorAuthentication.objects.create(
            user=instance,
            token=TwoFactorAuthentication.generate_otp_secret(),
        )
        instance.twofactorauthentication.generate_qr_code()