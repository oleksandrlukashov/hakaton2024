from django.urls import path
from .views import *

urlpatterns = [
    path('login/', UserLoginView.as_view()),
    path('otp-login/', OTPLoginView.as_view())
]
