from celery import shared_task
from django.utils import timezone
from django.db.models import Avg, Max, Min, Count
from datetime import datetime
from .models import City, WeatherData, DailyWeatherSummary
from .services import WeatherAPIService

@shared_task
def fetch_weather_data():
    api_service = WeatherAPIService(api_key='95e73333b1f491ae8676b1bb9588274a')
    for city in City.objects.all():
        weather_data = api_service.get_weather(city.name)
        WeatherData.objects.create(
            city=city,
            temperature=weather_data['main']['temp'],  # Already in Celsius
            feels_like=weather_data['main'].get('feels_like', None),  # Already in Celsius
            main_condition=weather_data['weather'][0]['main'],
            timestamp=timezone.make_aware(datetime.fromtimestamp(weather_data['dt']))  # Convert Unix timestamp to aware datetime
        )

@shared_task
def calculate_daily_summary():
    today = timezone.now().date()
    DailyWeatherSummary.objects.filter(date=today).delete()
    for city in City.objects.all():
        weather_data = WeatherData.objects.filter(city=city, timestamp__date=today)
        if weather_data.exists():
            avg_temp = weather_data.aggregate(Avg('temperature'))['temperature__avg']
            max_temp = weather_data.aggregate(Max('temperature'))['temperature__max']
            min_temp = weather_data.aggregate(Min('temperature'))['temperature__min']
            dominant_condition = weather_data.values('main_condition').annotate(count=Count('main_condition')).order_by('-count').first()['main_condition']
            DailyWeatherSummary.objects.create(
                city=city,
                date=today,
                avg_temperature=avg_temp,
                max_temperature=max_temp,
                min_temperature=min_temp,
                dominant_condition=dominant_condition
            )

@shared_task
def check_alerts():
    for city in City.objects.all():
        latest_weather = WeatherData.objects.filter(city=city).order_by('-timestamp').first()
        if latest_weather and latest_weather.temperature > 35:
            send_alert(city, latest_weather.temperature)

def send_alert(city, temperature):
    print(f"Alert! The temperature in {city.name} has exceeded 35°C. Current temperature: {temperature}°C")

