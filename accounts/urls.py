from unicodedata import name
from django.urls import path
from .views import (
        RegisterView, 
        VerifyUserEmail,
        LoginUserView, 
        TestingAuthenticatedReq, 
        PasswordResetConfirm, 
        PasswordResetRequestView,SetNewPasswordView, LogoutApiView,ChangePasswordRequestView,
        ResendOTPView,UserDetailsRetrieveUpdateDestroyView)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-phone/', VerifyUserEmail.as_view(), name='verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('changePassword/', ChangePasswordRequestView.as_view(), name='change-password'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('update-user/<int:id>/', UserDetailsRetrieveUpdateDestroyView.as_view(), name='user-details-retrieve-update-destroy'),
    path('get-something/', TestingAuthenticatedReq.as_view(), name='just-for-testing'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('change-phonenumber/', ResendOTPView.as_view(), name='change_phone_number'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
 
    ]