
from urllib.parse import urlencode
from rest_framework import serializers
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.response import Response
from .mixins import PublicApiMixin, ApiErrorsMixin
from accounts.utils import send_generated_otp_to_sms, resend_otp
from .utils import google_get_access_token, google_get_user_info, generate_tokens_for_user
from accounts.models import User, OneTimePassword
from rest_framework import status
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated


class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url=settings.BASE_FRONTEND_URL
    
        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}/')

        redirect_uri = settings.BASE_FRONTEND_URL
        access_token = google_get_access_token(code=code, 
                                               redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)
        try:
            user = User.objects.get(email=user_data['email'])
            access_token, refresh_token = generate_tokens_for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }
            print(response_data)
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            username = user_data['email'].split('@')[0]
            first_name = user_data.get('given_name', '')
            last_name = user_data.get('family_name', '')
            picture=user_data.get('picture','')
            user = User.objects.create(
                email=user_data['email'],
                first_name=first_name,
                last_name=last_name,
                profile_pic=picture,
                password=settings.GOOGLE_SIGNUP_PASS,
                auth_provider='google'
            )
            userId = UserSerializer(user).data.get("id")
            print(userId)
            print(picture)            
            access_token, refresh_token = generate_tokens_for_user(user)
            
            response_data = {
                'user': UserSerializer(user).data,
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }
            print(response_data)
            return Response(response_data, status=status.HTTP_200_OK)
class AddPhoneNumber(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        phone_number=request.data.get('phone_number')
        userId=request.data.get('user')
        user=User.objects.get(pk=userId)
        if phone_number and User.objects.filter(phone_number=phone_number).exclude(id=userId).exists():
            return Response({'message': 'This Phone number is already taken'}, status=status.HTTP_400_BAD_REQUEST)
        elif phone_number:
            user.phone_number=phone_number
            user.is_verified=False
            user.save()
            if OneTimePassword.objects.filter(user=userId).exists():
                resend_otp(phone_number=phone_number,user=userId, request=request)
            else:
             send_generated_otp_to_sms(phone_number, request)
            return Response({"message":"otp sent to your mobile number"},status=status.HTTP_200_OK)
        else:
            return Response({'error':'Please provide a valid phone number'},status=status.HTTP_400_BAD_REQUEST)
        
