from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

class WeatherData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    main_condition = models.CharField(max_length=50)
    timestamp = models.DateTimeField()

class DailyWeatherSummary(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date = models.DateField()
    avg_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_temperature = models.FloatField()
    dominant_condition = models.CharField(max_length=50)
