from django.core.management.base import BaseCommand
from air_quality.views import fetch_air_quality


class Command(BaseCommand):
    help = 'Fetches latest air quality data from WAQI API'
    
    def handle(self, *args, **options):
        fetch_air_quality()
        self.stdout.write("Successfully fetched air quality data")