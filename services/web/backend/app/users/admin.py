from django.contrib import admin
from .models import TwoFactorAuthentication, User

# Register your models here.
admin.site.register(TwoFactorAuthentication)
admin.site.register(User)