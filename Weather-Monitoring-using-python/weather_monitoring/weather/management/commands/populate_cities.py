# management/commands/populate_cities.py

from django.core.management.base import BaseCommand
from weather.models import City

class Command(BaseCommand):
    help = 'Populate the database with metro cities of India'

    def handle(self, *args, **kwargs):
        metro_cities = [
            "Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore", "Hyderabad",
            "Ahmedabad", "Pune", "Jaipur", "Surat", "Chandigarh", "Lucknow",
            "Kanpur", "Nagpur", "Indore", "Vadodara", "Bhopal", "Coimbatore",
            "Patna", "Visakhapatnam"
        ]

        for city_name in metro_cities:
            City.objects.get_or_create(name=city_name)

        self.stdout.write(self.style.SUCCESS('Successfully populated cities'))
