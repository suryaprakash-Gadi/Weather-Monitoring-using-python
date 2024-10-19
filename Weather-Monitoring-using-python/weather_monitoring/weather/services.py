import requests

class WeatherAPIService:
    def __init__(self, api_key):
        self.api_key = '95e73333b1f491ae8676b1bb9588274a'
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'
    
    def get_weather(self, city_name):
        params = {
            'q': city_name,
            'appid': self.api_key,
            'units': 'metric'  # for Celsius
        }
        response = requests.get(self.base_url, params=params)
        return response.json()
