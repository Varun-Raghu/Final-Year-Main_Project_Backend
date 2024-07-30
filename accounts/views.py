
from rest_framework.generics import GenericAPIView,  RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from accounts.models import OneTimePassword
from accounts.serializers import PasswordResetRequestSerializer,LogoutUserSerializer, UserRegisterSerializer, LoginSerializer, SetNewPasswordSerializer, ChangePasswordRequestSerializer
from rest_framework import status
from .utils import send_generated_otp_to_sms,resend_otp,send_normal_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated
from .models import User

class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user = request.data
        phone_number = user.get('phone_number')
        email = user.get('email')
        if User.objects.filter(email=email).exists() and User.objects.filter(phone_number=phone_number).exists():
            return Response({'message1': 'Phone number already exists','message2':'email already exists'})
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({'message1': 'Phone number already exists','message2':''})
        if User.objects.filter(email=email).exists():
            return Response({'message1': '','message2':'email already exists'})
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            send_generated_otp_to_sms(user_data['phone_number'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_id = request.data.get('user')
            user_pass_obj = OneTimePassword.objects.get(user=user_id)
            print(user_pass_obj)
            user = user_pass_obj.user
            print(passcode)
            print(user_pass_obj.otp)
            print(user)
            if user_pass_obj.otp == passcode:
                print(user_pass_obj.otp)
                if not user.is_verified:
                    user.is_verified = True
                    print('checked')
                    user.save()
                    return Response({
                        'message': 'Account Phone Number verified successfully'
                    }, status=status.HTTP_200_OK)
                return Response({'message': 'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({'message': 'provided the valid otp'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Return a response in case no other condition is met
        return Response({'message': 'passcode is invalid'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            serializer=self.serializer_class(data=request.data, context={'request':request})
            serializer.is_valid(raise_exception=True)
            return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        return Response({'message':'user with that email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordRequestView(GenericAPIView):
    serializer_class=ChangePasswordRequestSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)


class TestingAuthenticatedReq(GenericAPIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):

        data={
            'msg':'its works'
        }
        return Response(data, status=status.HTTP_200_OK)
    

class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
class ResendOTPView(GenericAPIView):
    def post(self,request):
        user=request.data['user']
        phone_number=request.data['phone_number']
        user_field = User.objects.get(id=user)
        resend_otp(phone_number,user, request)
        return Response({"message":f"OTP has been sent to your phone number:{phone_number}"})



class UserDetailsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        user=kwargs.get('id')
        email = request.data.get('email')
        if User.objects.filter(email=email).exclude(pk=user).exists():
            return Response({"message":"This email is already exist"}, status.HTTP_226_IM_USED)
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




