from django.shortcuts import render
import wikipediaapi
import requests
import datetime

def index(request):
    
    #API key and urls to OpenWeatherAPI
    api_key = 'API KEY FROM OPENWEATHERAPI GOES HERE'
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}'

    #Get city names and weather forecast and render to html
    if request.method == 'POST':

        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)

        weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, api_key, current_weather_url, forecast_url)
        city_info1 = get_summary(city1)

        if city2:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, api_key, current_weather_url, forecast_url)
            city_info2 = get_summary(city2)
        else:
            weather_data2, daily_forecasts2, city_info2 = None, None, None

        context = {
            'weather_data1': weather_data1,
            'city_info1' : city_info1,
            'daily_forecasts1': daily_forecasts1,
            'weather_data2': weather_data2,
            'city_info2' : city_info2,
            'daily_forecasts2': daily_forecasts2,
        }

        return render(request, 'weather_app/index.html', context)
    
    else:
        return render(request, 'weather_app/index.html')

#Get weather forecast and important information such as temperature etc
def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):

    response = requests.get(current_weather_url.format(city, api_key)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    weather_data = {
        'city': city,
        'temperature': round(response['main']['temp'] - 273.15, 2),
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }

    daily_forecasts = []

    for daily_data in forecast_response['list'][0:40:8]:
        daily_forecasts.append({
            'day': datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A'),
            'min_temp': round(daily_data['main']['temp_min'] - 273.15, 2),
            'max_temp': round(daily_data['main']['temp_max'] - 273.15, 2),
            'humidity': daily_data['main']['humidity'],
            'description': daily_data['weather'][0]['description'],
            'icon': daily_data['weather'][0]['icon'],
        })

    return weather_data, daily_forecasts

#Get summary of the city using Wikipedia API
def get_summary(city):
    
    wiki = wikipediaapi.Wikipedia('City Info', 'en')

    page_py = wiki.page(city)

    city_info = {
        'summary' : page_py.summary
    }

    return city_info