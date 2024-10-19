from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from .models import City, WeatherData, DailyWeatherSummary
from .tasks import fetch_weather_data, calculate_daily_summary, check_alerts
from .services import WeatherAPIService
from datetime import timedelta

class WeatherAPITests(TestCase):
    def setUp(self):
        self.city = City.objects.create(name='delhi')
        self.valid_api_key = '95e73333b1f491ae8676b1bb9588274a'
    
    @patch('requests.get')
    def test_system_setup(self, mock_get):
        mock_get.return_value.json.return_value = {
            'main': {'temp': 293.15, 'feels_like': 293.15},
            'weather': [{'main': 'Clear'}],
            'dt': timezone.now().timestamp()
        }
        
        api_service = WeatherAPIService(api_key=self.valid_api_key)
        response = api_service.get_weather(self.city.name)
        self.assertEqual(response['main']['temp'], 293.15)
    
    @patch('requests.get')
    @patch('django.utils.timezone.now')
    def test_data_retrieval(self, mock_now, mock_get):
        mock_get.return_value.json.return_value = {
            'main': {'temp': 293.15, 'feels_like': 293.15},
            'weather': [{'main': 'Clear'}],
            'dt': timezone.now().timestamp()
        }
        mock_now.return_value = timezone.now()

        fetch_weather_data()

        weather_data = WeatherData.objects.get(city=self.city)
        self.assertAlmostEqual(weather_data.temperature, 20.0)  # 293.15K to 20.0°C
        self.assertEqual(weather_data.main_condition, 'Clear')
    
    def test_temperature_conversion(self):
        temp_kelvin = 300
        temp_celsius = temp_kelvin - 273.15
        self.assertAlmostEqual(temp_celsius, 26.85)
    
    @patch('requests.get')
    def test_daily_weather_summary(self, mock_get):
        now = timezone.now()
        WeatherData.objects.create(
            city=self.city,
            temperature=20.0,
            feels_like=20.0,
            main_condition='Clear',
            timestamp=now - timedelta(days=1)
        )
        WeatherData.objects.create(
            city=self.city,
            temperature=21.0,
            feels_like=21.0,
            main_condition='Clear',
            timestamp=now
        )
        WeatherData.objects.create(
            city=self.city,
            temperature=19.0,
            feels_like=19.0,
            main_condition='Clear',
            timestamp=now
        )

        calculate_daily_summary()
        summary = DailyWeatherSummary.objects.get(city=self.city, date=now.date())
        
        self.assertAlmostEqual(summary.avg_temperature, 20.0)  # Average of 19.0, 20.0, and 21.0
        self.assertEqual(summary.max_temperature, 21.0)  # Maximum temperature
        self.assertEqual(summary.min_temperature, 19.0)  # Minimum temperature
        self.assertEqual(summary.dominant_condition, 'Clear')
    
    @patch('requests.get')
    @patch('builtins.print')
    def test_alerting_thresholds(self, mock_print, mock_get):
        now = timezone.now()
        WeatherData.objects.create(
            city=self.city,
            temperature=36.0,
            feels_like=36.0,
            main_condition='Hot',
            timestamp=now
        )

        check_alerts()
        mock_print.assert_called_once_with(
            f"Alert! The temperature in {self.city.name} has exceeded 35°C. Current temperature: 36.0°C"
        )
    
    @patch('requests.get')
    def test_bonuses(self, mock_get):
        mock_get.return_value.json.return_value = {
            'main': {'temp': 293.15, 'humidity': 70},
            'wind': {'speed': 5.5},
            'weather': [{'main': 'Clear'}],
            'dt': timezone.now().timestamp()
        }
        fetch_weather_data()
        weather_data = WeatherData.objects.get(city=self.city)
        self.assertEqual(weather_data.humidity, 70)
        self.assertEqual(weather_data.wind_speed, 5.5)
