from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import pyotp
import qrcode
from io import BytesIO
import os

# Create your models here.
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False,
                                   verbose_name='is_staff (позволяет заходить пользователю в админку)')  # must needed, otherwise you won't be able to loginto django-admin.
    is_superuser = models.BooleanField(default=False,
                                       verbose_name='is_superuser (дает права админа)')  # this field we inherit from PermissionsMixin.

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class TwoFactorAuthentication(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=16)
    qrcode = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return f"2FA for {self.user.id}"

    @staticmethod
    def generate_otp_secret():
        """Generate a random OTP secret."""
        return pyotp.random_base32()

    def generate_qr_code(self):
        """Generate a QR code for the user's TOTP configuration."""
        totp = pyotp.TOTP(self.token)
        link = totp.provisioning_uri(self.user.email, issuer_name="MyApp")
        
        # Generate the QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(link)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Save QR code to a file
        image_file = BytesIO()
        qr_image.save(image_file, format='PNG')
        file_name = f"qrcodes/{self.user.id}_2fa.png"

        path = os.path.join('media', file_name)
        with open(path, 'wb') as f:
            f.write(image_file.getvalue())

        self.qrcode = file_name
        self.save()

    def verify_otp(self, otp):
        """Verify the provided OTP using the user's secret token."""
        totp = pyotp.TOTP(self.token)
        return totp.verify(otp)


    def delete(self, *args, **kwargs):
        """Delete the image file from the filesystem before deleting the object."""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        super().delete(*args, **kwargs)