from django.shortcuts import render
from weather.tasks import calculate_daily_summary
from .models import DailyWeatherSummary
from django.utils import timezone

def dashboard_view(request):
    calculate_daily_summary()

    unit = request.GET.get('unit', 'celsius')  # Default to Celsius
    summaries = DailyWeatherSummary.objects.all().order_by('-date')

    if unit == 'fahrenheit':
        for summary in summaries:
            summary.avg_temperature = summary.avg_temperature * 9/5 + 32
            summary.max_temperature = summary.max_temperature * 9/5 + 32
            summary.min_temperature = summary.min_temperature * 9/5 + 32
    elif unit == 'kelvin':
        for summary in summaries:
            summary.avg_temperature = summary.avg_temperature + 273.15
            summary.max_temperature = summary.max_temperature + 273.15
            summary.min_temperature = summary.min_temperature + 273.15

    return render(request, 'dashboard.html', {
        'summaries': summaries,
        'unit': unit,
    })

