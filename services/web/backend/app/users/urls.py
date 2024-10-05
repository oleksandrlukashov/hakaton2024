from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', UserLoginAPIView.as_view()),
    path('otp-login/', OTPLoginAPIView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('logout/', LogoutAPIView.as_view())
]
