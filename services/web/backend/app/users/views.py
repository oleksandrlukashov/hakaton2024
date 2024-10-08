from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import User
from .serializers import UserLoginSerializer, OTPLoginSerializer, LogoutSerializer

# Create your views here.
class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            return Response({
                'message': 'Success',
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "access": serializer.validated_data['access'],
                "refresh": serializer.validated_data['refresh'],
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)