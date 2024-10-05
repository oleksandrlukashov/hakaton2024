from django.test import TestCase
from .models import User
from rest_framework.test import APIClient
from rest_framework import status
import pyotp
from .models import TwoFactorAuthentication

class UserLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(password='testpassword', email="test@example.com")
    
    def test_login_with_valid_credentials(self):
        response = self.client.post('/api/users/login/', {'email': 'test@example.com', 'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)

    def test_login_with_invalid_credentials(self):
        response = self.client.post('/api/users/login/', {'email': 'test@example.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OTPLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpassword')
        self.two_fa = TwoFactorAuthentication.objects.create(user=self.user, token=pyotp.random_base32())
    
    def test_otp_login_with_valid_otp(self):
        # Generate a valid OTP using pyotp
        totp = pyotp.TOTP(self.two_fa.token)
        valid_otp = totp.now()

        response = self.client.post('/api/users/otp-login/', {'id': self.user.id, 'token': valid_otp})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['message'], 'Login successful')

    def test_otp_login_with_invalid_otp(self):
        response = self.client.post('/api/users/otp-login/', {'id': self.user.id, 'token': '123456'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
