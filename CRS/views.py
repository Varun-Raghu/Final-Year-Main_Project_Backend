from django.shortcuts import render
from .models import *
# from accounts.models import Landmark
from .utils import get_prediction,get_weather_data,crop_yield_pred,get_fertilizer_recommendation
from rest_framework.generics import GenericAPIView, ListCreateAPIView,RetrieveDestroyAPIView
from .serializers import CropRecommendationSerializer,LandmarkSerializer,CropYieldPredictionSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Landmark
from rest_framework.views import APIView
from rest_framework.response import Response
from pusher import Pusher
from .utils import get_weather_data,pushbullet_message
import os
from django.conf import settings
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views import View
from pusher import Pusher
import threading
import time


# class LandmarkDetailAPIView(RetrieveDestroyAPIView):
#     queryset = Landmark.objects.all()
#     serializer_class = LandmarkSerializer

#     def delete(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         self.perform_destroy(instance)
#         return Response(serializer.data)
    
class ListCreateLandmarkAPIView(GenericAPIView):
    queryset = Landmark.objects.all()
    serializer_class = LandmarkSerializer

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = User.objects.get(pk=user_id)

        landmarks = Landmark.objects.filter(user_id=user)
        serializer = self.get_serializer(landmarks, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            pushbullet_message(title="Land Coords", body=f"{serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CropRecomendationApiView(APIView):
    serializer_class = CropRecommendationSerializer

    def post(self, request):
        crop_data = request.data
        user = crop_data.get('user')
        landId = crop_data.get('landId')

        try:
            # Fetch Landmark object based on user and landId
            landmark = Landmark.objects.get(user=user, landId=landId)

            # Access coordinates from the Landmark object
            coordinates = landmark.coordinates

            # Calculate median latitude and longitude
            latitudes = [coord['lat'] for coord in coordinates]
            longitudes = [coord['lng'] for coord in coordinates]

            median_latitude = sum(latitudes) / len(latitudes)
            median_longitude = sum(longitudes) / len(longitudes)

            # Fetch weather data based on the median coordinates
            weather_data = get_weather_data(median_latitude, median_longitude)

            if weather_data:
                # Process crop recommendation data using weather data
                n = crop_data.get('nitrogen')
                p = crop_data.get('phosphorus')
                k = crop_data.get('potassium')
                ph = crop_data.get('ph')
                prediction = get_prediction(N=n, P=p, K=k, temperature=weather_data['temp_c'], humidity=weather_data['humidity'], ph=ph, rainfall=weather_data['rainfall'], request=request)

                # Prepare data for serialization
                data = { 
                    "user": user,
                    "landId": landId, 
                    "N": n, 
                    "P": p, 
                    "K": k, 
                    "temperature": weather_data['temp_c'],  
                    "humidity": weather_data['humidity'], 
                    "ph": ph, 
                    "rainfall": weather_data['rainfall'],
                    "prediction": prediction
                }
                pushbullet_message(title="Agro Harvest Recommendation", body=f"The Recommended Crop is {data['prediction']}")
                # Serialize the data
                serializer = self.serializer_class(data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    user_data = serializer.data
                    return Response({
                        'data': user_data,
                        'message': 'Thanks for using our Recommendation System'
                    }, status=status.HTTP_201_CREATED)

            else:
                return Response({'success': False, 'message': 'Weather data not available'}, status=status.HTTP_400_BAD_REQUEST)

        except Landmark.DoesNotExist:
            return Response({'success': False, 'message': 'Landmark not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CropYieldPredictionView(APIView):
    def post(self, request, *args, **kwargs):
        crop_data = request.data

        # Extract data from the request
        user = crop_data.get('user')
        landId =crop_data.get('landId')
        year = int(crop_data.get('year'))
        season = crop_data.get('season')
        month = int(crop_data.get('month'))
        crop_type = int(crop_data.get('crop'))
        area = float(crop_data.get('area'))
        print("user:", user, type(user))
        print("landId:", landId, type(landId))
        print("year:", year, type(year))
        print("season:", season, type(season))
        print("month:", month, type(month))
        print("crop_type:", crop_type, type(crop_type))
        print("area:", area, type(area))

        # Check if the 'year' field is not null
        if not year:
            return Response({'success': False, 'message': 'Year is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the Landmark exists
            landmark = Landmark.objects.get(user=user, landId=landId)

            # Access coordinates from the Landmark object
            coordinates = landmark.coordinates

            # Calculate median latitude and longitude
            latitudes = [coord['lat'] for coord in coordinates]
            longitudes = [coord['lng'] for coord in coordinates]

            median_latitude = sum(latitudes) / len(latitudes)
            median_longitude = sum(longitudes) / len(longitudes)

            # Fetch weather data based on the median coordinates
            weather_data = get_weather_data(median_latitude, median_longitude)

            if weather_data:
                # Predict crop yield
                result = crop_yield_pred(year, season, month, crop_type, area,
                                         avg_temp=weather_data['temp_c'],
                                         avg_rainfall=weather_data['rainfall'])

                # Send push notification
                pushbullet_message(title="Agro Harvest yield prediction",
                                   body=f"The predicted Crop yield for {month} months is {result['yield']}")

                return Response({
                    'production': result.get("production"),
                    'yield_per_hectare': result.get("yield"),
                    'message': 'Crop yield prediction successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'Weather data not available'},
                                status=status.HTTP_400_BAD_REQUEST)

        except Landmark.DoesNotExist:
            return Response({'success': False, 'message': 'Landmark not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FertilizerRecommendation(APIView):
    def post(self, request, format=None):
        # Extract data from the request
        
        temperature = request.data.get('temperature')
        humidity = request.data.get('humidity')
        moisture = request.data.get('moisture')
        soil_type = request.data.get('soil_type')
        crop_type = request.data.get('crop_type')
        nitrogen = request.data.get('nitrogen')
        phosphorous = request.data.get('phosphorous')
        potassium = request.data.get('potassium')

        # Call the utility function to get the fertilizer recommendation
        recommendation = get_fertilizer_recommendation(request=request,crop_type=crop_type, nitrogen=nitrogen, phosphorous=phosphorous, potassium=potassium,temperature=temperature,humidity=humidity,soil_type=soil_type,moisture=moisture)
        pushbullet_message(title="Agro Harvest Fertilizer Recommendation", body=f"The Recommended Fertilizer is {recommendation['name']}")
        # Return the recommendation as a response
        return Response({"recommendation": recommendation}, status=status.HTTP_200_OK)
    






pusher_client = Pusher(
    app_id='1800023',
    key='d26e14d5cf68e9a279b4',
    secret='eecba1e8a015aa79de26',
    cluster='mt1',
    ssl=True
)

class PusherEventTrigger(View):
    def get(self, request):
        try:
            # Trigger Pusher event
            pusher_client.trigger('my-channel', 'my-event', {'message': "hello world"})
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def auto_trigger(self):
        while True:
            time.sleep(60)  # Sleep for 60 seconds (1 minute)
            try:
                # Trigger Pusher event
                pusher_client.trigger('my-channel', 'my-event', {'message': "hello world"})
            except Exception as e:
                print(f"Error triggering Pusher event: {e}")

# Start the auto-trigger thread
auto_trigger_thread = threading.Thread(target=PusherEventTrigger().auto_trigger)
auto_trigger_thread.daemon = True
auto_trigger_thread.start()