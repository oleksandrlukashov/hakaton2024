from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import TwoFactorAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(email=email, password=password)
        print(user)

        if user is None:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive")

        data['user'] = user
        return data
    

class OTPLoginSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    token = serializers.CharField(max_length=6)

    def validate(self, data):
        user_id = data.get('id')
        token = data.get('token')

        if not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError("User not found.")

        user = User.objects.get(id=user_id)

        if not TwoFactorAuthentication.objects.filter(user=user).exists():
            raise serializers.ValidationError("2FA not set up for this user.")

        two_factor_auth = TwoFactorAuthentication.objects.get(user=user)

        if not two_factor_auth.verify_otp(token):
            raise serializers.ValidationError("Invalid OTP.")

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        data['refresh'] = str(refresh)
        data['access'] = str(access_token)
        return data
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        token = RefreshToken(value)

        if not token:
            raise serializers.ValidationError("Invalid or expired refresh token.")
        
        token.blacklist()

        return True