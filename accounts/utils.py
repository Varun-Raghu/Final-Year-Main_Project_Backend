
from django.core.mail import EmailMessage
import random
import requests
from django.conf import settings
from .models import User, OneTimePassword



def send_generated_otp_to_sms(phone_number, request): 
    otp=random.randint(100000, 999999) 
    user = User.objects.get(phone_number=phone_number)
    otp_obj=OneTimePassword.objects.create(user=user, otp=otp)
    api_key = settings.TWO_FACTOR_API_KEY
    api_url = f"https://2factor.in/API/V1/{api_key}/SMS/{user.phone_number}/{otp}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        json_response = response.json()
        if json_response['Status'] == 'Success':
            print("OTP Sent successfully. Session ID:", json_response['Details'])
        else:
            return Exception(f"Failed to send OTP. Reason: {json_response['Details']}")
    except requests.RequestException as e:
        return Exception(f"Request to 2Factor.in failed. Reason: {str(e)}")
    except Exception as e:
        return e
   
def resend_otp(phone_number,user,request):
    otp=random.randint(100000, 999999) 
    currentOtp = OneTimePassword.objects.get(user=user)
    currentOtp.otp = otp
    currentOtp.save()
    api_key = settings.TWO_FACTOR_API_KEY
    api_url = f"https://2factor.in/API/V1/{api_key}/SMS/{phone_number}/{otp}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        json_response = response.json()
        if json_response['Status'] == 'Success':
            print("OTP Sent successfully. Session ID:", json_response['Details'])
        else:
            return Exception(f"Failed to send OTP. Reason: {json_response['Details']}")
    except requests.RequestException as e:
        return Exception(f"Request to 2Factor.in failed. Reason: {str(e)}")
    except Exception as e:
        return e



def send_normal_email(data):

    message = data.get('email_body', '')
    subject = data.get('email_subject', '')
    receiver = data.get('to_email', '')
    from_email = data.get('from_email', '')
    # Now you can use these variables as needed

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=[receiver],
    )
    email.send()


