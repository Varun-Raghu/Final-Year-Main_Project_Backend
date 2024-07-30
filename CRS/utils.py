import pickle
import numpy as np
import pandas as pd
import requests
from django.conf import settings
import os
import requests
from bs4 import BeautifulSoup
import json
# Load the Random Forest model from the pickle file
def pushbullet_message(title, body, icon_url=None):
    # Create message payload
    msg = {"type": "note", "title": title, "body": body}
    
    # If an icon URL is provided, include it in the message payload
    if icon_url:
        msg["file_url"] = icon_url
    
    # Pushbullet API authentication token
    TOKEN = 'o.DS4bR9tCAIgOsVE9YKZQXqI3G4EE49Y2'
    
    # Send the message
    resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + TOKEN,
                                  'Content-Type': 'application/json'})
    
    # Check the response status code
    if resp.status_code != 200:
        raise Exception('Error', resp.status_code)
    else:
        print('Message sent')

def get_weather_data(latitude, longitude):
    api_key = '31a8d1a6588a42a78ff115005242702'  # Replace with your WeatherAPI key
    base_url = 'http://api.weatherapi.com/v1/current.json'
    params = {'key': api_key, 'q': f'{latitude},{longitude}'}
   
    response = requests.get(base_url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"Error from WeatherAPI: {data['error']['message']}")
        return None

    print(f"WeatherAPI Response: {data}")
   
    weather_data = {
        'city': data['location']['name'],
        'last_updated': data['current']['last_updated'],
        'temp_c': data['current']['temp_c'],
        'temp_f': data['current']['temp_f'],
        'is_day': data['current']['is_day'],
        'text': data['current']['condition']['text'],
        'icon': data['current']['condition']['icon'],
        'wind_mph': data['current']['wind_mph'],
        'wind_kph': data['current']['wind_kph'],
        'wind_degree': data['current']['wind_degree'],
        'wind_dir': data['current']['wind_dir'],
        'pressure_mb': data['current']['pressure_mb'],
        'pressure_in': data['current']['pressure_in'],
        'rainfall': data['current']['precip_mm'],
        'precip_in': data['current']['precip_in'],
        'humidity': data['current']['humidity'],
        'cloud': data['current']['cloud'],
        'feelslike_c': data['current']['feelslike_c'],
        'feelslike_f': data['current']['feelslike_f'],
        'vis_km': data['current']['vis_km'],
        'vis_miles': data['current']['vis_miles'],
        'gust_mph': data['current']['gust_mph'],
        'gust_kph': data['current']['gust_kph'],
        'uv': data['current']['uv'],
    }
    return weather_data

def get_prediction(request,N,P,K,temperature,humidity,ph,rainfall):
    model_path = os.path.join(settings.BASE_DIR, 'CRS', 'models', 'model.pkl')
    with open(model_path, 'rb') as f:
        RF = pickle.load(f)
    

    data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

    # Make prediction using the loaded model
    prediction = RF.predict(data)

    # Output the prediction
    print(f"The recommended crop is {prediction[0]}")

    return prediction[0]

def crop_yield_pred(year, season, month, crop, area, avg_temp, avg_rainfall):
    model_path = os.path.join(settings.BASE_DIR, 'CRS', 'models', 'cyp_model.pkl')
    with open(model_path, 'rb') as f:
        CYP = pickle.load(f)
    
    data = np.array([[area, crop, year, avg_rainfall, season, avg_temp]])

    # Make prediction using the loaded model
    production = int(CYP.predict(data)[0]) / int(month)
    yield_value = production / int(area)

    # Round the values to two decimal places
    production_rounded = round(production, 2)
    yield_rounded = round(yield_value, 2)

    return {"production": production_rounded, "yield": yield_rounded}




def get_fertilizer_recommendation(request, temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous):
    model_path = os.path.join(settings.BASE_DIR, 'CRS', 'models', 'rf_pipeline.pkl')
    with open(model_path, 'rb') as f:
        rf_pipeline = pickle.load(f)
    
    data = np.array([[temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous]])
    prediction = rf_pipeline.predict(data)
    recommendation = prediction[0]

    # Fertilizer labels
    fertilizer_labels = ['Urea', 'DAP', '14-35-14', '28-28', '17-17-17', '20-20', '10-26-26']

    fertilizer = {
    0:"Urea is a nitrogen-rich fertilizer, containing approximately 46% nitrogen. It is one of the most widely used fertilizers due to its high nitrogen content and affordability.Urea is suitable for a variety of crops including grains, vegetables, fruits, and grasslands. It is commonly used as a nitrogen source for plants to promote vegetative growth.Apply urea evenly to the soil around the base of plants. Avoid direct contact with plant foliage to prevent leaf burn. Incorporate urea into the soil through watering or mechanical means for better absorption. The recommended dosage varies depending on the crop and soil conditions.",
    1:"Diammonium phosphate (DAP) is a widely used phosphorus fertilizer containing high levels of phosphorus (typically 18-46% P2O5) and nitrogen in the form of ammonia. It is highly soluble in water, making it readily available to plants.DAP is suitable for a variety of crops, especially those with high phosphorus requirements, such as fruits, vegetables, and grains. It is commonly used during the early stages of plant growth to promote root development and overall plant vigor.Apply DAP evenly to the soil before planting or as a side dressing during the growing season. Mix it thoroughly with the soil to ensure proper distribution of phosphorus. Avoid direct contact with plant roots to prevent root burn. Follow recommended application rates based on soil test results or crop requirements.",
    2:"The 14-35-14 fertilizer is a phosphorus-rich fertilizer with a balanced ratio of nitrogen (N), phosphorus (P), and potassium (K). It typically contains 14% nitrogen, 35% phosphorus pentoxide (P2O5), and 14% potassium oxide (K2O). This formulation provides a high concentration of phosphorus, which is essential for root development, flowering, and fruit formation.14-35-14 fertilizer is suitable for crops with high phosphorus requirements, such as flowering plants, fruits, and vegetables. It is particularly beneficial during the early stages of plant growth and flowering to promote vigorous root growth and enhance flower and fruit production.Apply 14-35-14 fertilizer evenly to the soil before planting or as a side dressing during the growing season. Incorporate it into the soil to ensure proper root uptake of nutrients. Follow recommended application rates based on soil test results or crop requirements. Avoid overapplication to prevent nutrient imbalances and potential harm to plants.",
    3:"The 28-28 fertilizer is a balanced fertilizer with equal parts of nitrogen (N), phosphorus (P), and potassium (K). It typically contains 28% nitrogen, 28% phosphorus pentoxide (P2O5), and 28% potassium oxide (K2O). This formulation provides essential nutrients for overall plant growth and development.28-28 fertilizer is suitable for a wide range of crops, including vegetables, fruits, flowers, and ornamental plants. It is particularly beneficial during the growing season to promote healthy foliage, root development, and flowering.Apply 28-28 fertilizer evenly to the soil before planting or as a top dressing during the growing season. Incorporate it into the soil to ensure proper nutrient uptake by plant roots. Follow recommended application rates based on soil test results or crop requirements. Avoid overapplication to prevent nutrient imbalances and potential harm to plants",
    4:"The 17-17-17 fertilizer is a balanced fertilizer with equal proportions of nitrogen (N), phosphorus (P), and potassium (K). It typically contains 17% nitrogen, 17% phosphorus pentoxide (P2O5), and 17% potassium oxide (K2O). This balanced formulation provides essential nutrients for overall plant growth, flowering, and fruiting.17-17-17 fertilizer is suitable for a wide range of crops, including vegetables, fruits, grains, and ornamental plants. It is particularly beneficial during the growing season to promote healthy foliage, root development, and flowering.Apply 17-17-17 fertilizer evenly to the soil before planting or as a top dressing during the growing season. Incorporate it into the soil to ensure proper nutrient distribution and uptake by plant roots. Follow recommended application rates based on soil test results or crop requirements. Avoid overapplication to prevent nutrient imbalances and potential harm to plants.",
    5:"The 20-20 fertilizer is a balanced fertilizer with equal proportions of nitrogen (N), phosphorus (P), and potassium (K). It typically contains 20% nitrogen, 20% phosphorus pentoxide (P2O5), and 20% potassium oxide (K2O). This balanced formulation provides essential nutrients for overall plant growth, flowering, and fruiting.20-20 fertilizer is suitable for a wide range of crops, including vegetables, fruits, grains, and ornamental plants. It is particularly beneficial during the growing season to promote healthy foliage, root development, and flowering.xApply 20-20 fertilizer evenly to the soil before planting or as a top dressing during the growing season. Incorporate it into the soil to ensure proper nutrient distribution and uptake by plant roots. Follow recommended application rates based on soil test results or crop requirements. Avoid overapplication to prevent nutrient imbalances and potential harm to plants.",
    6:"The 10-26-26 fertilizer is a phosphorus and potassium-rich fertilizer with a lower proportion of nitrogen. It typically contains 10% nitrogen, 26% phosphorus pentoxide (P2O5), and 26% potassium oxide (K2O). This formulation is ideal for promoting root development, flowering, and fruiting in plants.10-26-26 fertilizer is suitable for crops with high phosphorus and potassium requirements, such as flowering plants, fruit-bearing trees, and root vegetables. It is particularly beneficial during the flowering and fruiting stages to enhance flower and fruit production.Apply 10-26-26 fertilizer evenly to the soil before planting or during the flowering and fruiting stages of growth. Incorporate it into the soil to ensure proper root uptake of nutrients. Follow recommended application rates based on soil test results or crop requirements. Avoid overapplication to prevent nutrient imbalances and potential harm to plants."
}
    recommended_fertilizer = {"fertilizer":fertilizer[recommendation],"name":fertilizer_labels[recommendation]}

    # Scrape fertilizer standards and content from a reliable source

    
    return recommended_fertilizer
