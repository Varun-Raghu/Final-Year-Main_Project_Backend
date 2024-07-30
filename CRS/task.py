# tasks.py
from rq import get_current_job
from time import sleep
from firebase_admin import credentials, initialize_app, messaging  # Import Firebase Admin SDK
from .utils import get_weather_data
import os
from django.conf import settings

def send_push_notification_to_user(user_email="vijayanand.15012003@gmail.com"):
    try:
        # Initialize Firebase Admin SDK
        firebase_cred_path = os.path.join(settings.BASE_DIR, 'CRS', 'models', 'crsfirebase.json')  # Path to your Firebase credentials JSON file
        cred = credentials.Certificate(firebase_cred_path)
        initialize_app(cred)

        # Fetch weather data
        latitude = 40.7128  # Example latitude
        longitude = -74.0060  # Example longitude
        weather_data = get_weather_data(latitude, longitude)

        # Create notification message
        notification_message = f"Weather in {weather_data['city']}: {weather_data['text']}, Temperature: {weather_data['temp_c']}°C"

        # Send push notification using Firebase Cloud Messaging
        message = messaging.Message(
            notification=messaging.Notification(
                title='Weather Update',
                body=notification_message
            ),
            token=user_email  # Token here can be the device token or the registration token of the user
        )
        response = messaging.send(message)

        print("Push notification sent successfully.")
    except Exception as e:
        print(f"Error sending push notification: {str(e)}")
