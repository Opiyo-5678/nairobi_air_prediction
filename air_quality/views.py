import requests
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
from .models import AirQualityStation, AirQualityReading
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from io import BytesIO

# Predefined monitoring stations across Nairobi
# In a real implementation, you would get these from a database or another API
NAIROBI_STATIONS = [
    {"name": "Nairobi CBD", "lat": -1.286389, "lon": 36.817223},
    {"name": "Westlands", "lat": -1.267248, "lon": 36.803504},
    {"name": "Kibera", "lat": -1.315991, "lon": 36.783333},
    {"name": "Karen", "lat": -1.317210, "lon": 36.706086},
    {"name": "Eastleigh", "lat": -1.270556, "lon": 36.845556},
    {"name": "Kileleshwa", "lat": -1.278515, "lon": 36.781291},
    {"name": "Kilimani", "lat": -1.289680, "lon": 36.785830},
    {"name": "Langata", "lat": -1.326460, "lon": 36.758710},
    {"name": "Embakasi", "lat": -1.328569, "lon": 36.903946},
    {"name": "Ruaraka", "lat": -1.231078, "lon": 36.857632},
    {"name": "Roysambu", "lat": -1.217834, "lon": 36.877161},
    {"name": "Kasarani", "lat": -1.222222, "lon": 36.893333},
    {"name": "South B", "lat": -1.306998, "lon": 36.833244},
    {"name": "South C", "lat": -1.313817, "lon": 36.824112},
    {"name": "Huruma", "lat": -1.254722, "lon": 36.867222},
    {"name": "Kahawa", "lat": -1.184433, "lon": 36.928144},
    {"name": "Kariobangi", "lat": -1.257812, "lon": 36.878844},
    {"name": "Parklands", "lat": -1.260908, "lon": 36.810998},
    {"name": "Ngara", "lat": -1.274847, "lon": 36.827877},
    {"name": "Dagoretti", "lat": -1.298750, "lon": 36.737775},
    {"name": "Umoja", "lat": -1.280277, "lon": 36.892224},
    {"name": "Donholm", "lat": -1.291417, "lon": 36.880000},
    {"name": "Pipeline", "lat": -1.316667, "lon": 36.883333},
    {"name": "Utawala", "lat": -1.293889, "lon": 36.954444},
    {"name": "Kayole", "lat": -1.272222, "lon": 36.916667},
    {"name": "Madaraka", "lat": -1.308889, "lon": 36.815000},
    {"name": "Dandora", "lat": -1.248611, "lon": 36.886944},
    {"name": "Mathare", "lat": -1.257500, "lon": 36.857500},
    {"name": "Zimmerman", "lat": -1.208056, "lon": 36.886944},
    {"name": "Kangemi", "lat": -1.261111, "lon": 36.745278}
]

@login_required(login_url='/auth/login/')
def air_quality_page(request):
    """Render the main air quality page with the map"""
# Set initial map center (Nairobi CBD)
    initial_lat = -1.286389
    initial_lon = 36.817223

    context = {
        'initial_lat': initial_lat,
        'initial_lon': initial_lon,
    }
    
    return render(request, 'air_quality.html', context)


@login_required(login_url='/auth/login/')
def get_air_quality_data(request):
    """API endpoint to fetch air quality data for all stations"""
    api_key = "8d7134bd47dfec19a3a6120c52d3906e7da3e30b"  # Your WAQI API key
    
    air_quality_data = []
    
    # Make sure all stations exist in the database
    for station_info in NAIROBI_STATIONS:
        station, created = AirQualityStation.objects.get_or_create(
            name=station_info['name'],
            defaults={
                'latitude': station_info['lat'],
                'longitude': station_info['lon']
            }
        )
        
        # Use geo coordinates to get nearest station data
        api_url = f"https://api.waqi.info/feed/geo:{station_info['lat']};{station_info['lon']}/"
        
        try:
            response = requests.get(f"{api_url}?token={api_key}")
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok':
                    # Some stations might not have all data fields
                    # Use get() with default values to handle missing data
                    station_data = {
                        'name': station_info['name'],
                        'aqi': data['data'].get('aqi', 'N/A'),
                        'latitude': station_info['lat'],
                        'longitude': station_info['lon'],
                        'dominant_pollutant': 'pm2.5',  # Override dominant pollutant to PM2.5
                        'timestamp': data['data'].get('time', {}).get('s', 'N/A'),
                    }
                    
                    # Extract pollutant details if available
                    pollutants = {}
                    if 'iaqi' in data['data']:
                        for pollutant, value in data['data']['iaqi'].items():
                            if 'v' in value:
                                pollutants[pollutant] = value['v']
                        station_data['pollutants'] = pollutants
                    
                    air_quality_data.append(station_data)
                    
                    # Convert timestamp string to datetime object
                    try:
                        if station_data['timestamp'] != 'N/A':
                            # Parse the timestamp format from the API
                            timestamp = datetime.strptime(station_data['timestamp'], '%Y-%m-%d %H:%M:%S')
                        else:
                            # Use current time if no timestamp is provided
                            timestamp = timezone.now()
                            
                        # Store reading in database
                        reading, created = AirQualityReading.objects.get_or_create(
                            station=station,
                            timestamp=timestamp,
                            defaults={
                                'aqi': None if station_data['aqi'] == 'N/A' else station_data['aqi'],
                                'dominant_pollutant': station_data['dominant_pollutant'],  # Override dominant pollutant
                                'pm25': pollutants.get('pm2.5'),
                                'pm10': pollutants.get('pm10'),
                                'o3': pollutants.get('o3'),
                                'no2': pollutants.get('no2'),
                                'so2': pollutants.get('so2'),
                                'co': pollutants.get('co'),
                                'humidity': pollutants.get('h'),
                                'temperature': pollutants.get('t'),
                                'pressure': pollutants.get('p'),
                                'wind': pollutants.get('w')
                            }
                        )
                        
                        if not created:
                            # Update existing reading if needed
                            reading.aqi = None if station_data['aqi'] == 'N/A' else station_data['aqi']
                            reading.dominant_pollutant = station_data['dominant_pollutant']  # Override dominant pollutant
                            reading.pm25 = pollutants.get('pm2.5')
                            reading.pm10 = pollutants.get('pm10')
                            reading.o3 = pollutants.get('o3')
                            reading.no2 = pollutants.get('no2')
                            reading.so2 = pollutants.get('so2')
                            reading.co = pollutants.get('co')
                            reading.humidity = pollutants.get('h')
                            reading.temperature = pollutants.get('t')
                            reading.pressure = pollutants.get('p')
                            reading.wind = pollutants.get('w')
                            reading.save()
                            
                    except Exception as e:
                        print(f"Error saving reading to database: {str(e)}")
            
        except Exception as e:
            # In production, you would log this error
            print(f"Error fetching data for {station_info['name']}: {str(e)}")
            # Add a placeholder with error info
            air_quality_data.append({
                'name': station_info['name'],
                'aqi': 'Error',
                'latitude': station_info['lat'],
                'longitude': station_info['lon'],
                'error': str(e)
            })
    
    return JsonResponse({'air_quality_data': air_quality_data})

@login_required(login_url='/auth/login/')
def historical_data(request):
    return render(request, 'dashboard.html')

@login_required(login_url='/auth/login/')
def air_quality_api(request):
    station_id = request.GET.get('station', 'all')
    days = int(request.GET.get('days', 7))
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Filter readings by time (and station if specified)
    readings = AirQualityReading.objects.filter(
        timestamp__range=(start_date, end_date)
    )
    if station_id != 'all':
        readings = readings.filter(station_id=station_id)
    
    # Calculate AQI distribution (simplified example)
    def calculate_aqi_distribution(readings):
        categories = [0, 0, 0, 0, 0, 0]  # Good, Moderate, etc.
        for r in readings:
            if not r.aqi: continue
            if r.aqi <= 50: categories[0] += 1
            elif r.aqi <= 100: categories[1] += 1
            elif r.aqi <= 150: categories[2] += 1
            elif r.aqi <= 200: categories[3] += 1
            elif r.aqi <= 300: categories[4] += 1
            else: categories[5] += 1
        return categories
    
    # Prepare the response
    data = {
        "timestamps": [r.timestamp.strftime('%Y-%m-%d %H:%M') for r in readings],
        "pm2.5": [r.pm25 for r in readings],
        "pm10": [r.pm10 for r in readings],
        "no2": [r.no2 for r in readings],
        "o3": [r.o3 for r in readings],
        "avg_pm25": readings.aggregate(Avg('pm25'))['pm25__avg'] or 0,
        "avg_pm10": readings.aggregate(Avg('pm10'))['pm10__avg'] or 0,
        "avg_no2": readings.aggregate(Avg('no2'))['no2__avg'] or 0,
        "avg_o3": readings.aggregate(Avg('o3'))['o3__avg'] or 0,
        "latest": {
            "aqi": readings.last().aqi if readings.exists() else None,
            "pm2.5": readings.last().pm25 if readings.exists() else None,
            "pm10": readings.last().pm10 if readings.exists() else None,
            "temperature": readings.last().temperature if readings.exists() else None,
            "humidity": readings.last().humidity if readings.exists() else None,
            "dominant_pollutant": readings.last().dominant_pollutant if readings.exists() else None,
            "timestamp": readings.last().timestamp.strftime('%Y-%m-%d %H:%M') if readings.exists() else None,
        },
        "aqi_distribution": calculate_aqi_distribution(readings),
    }
    return JsonResponse(data)


def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')
def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        # Basic validation
        if not all([name, email, subject, message]):
            messages.error(request, 'All fields are required')
            return render(request, 'contact_us.html')
        
        try:
            send_mail(
                subject=f"New Contact: {subject}",
                message=f"From: {name} <{email}>\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
          #  messages.success(request, 'Your message has been sent successfully!')
            return redirect('air_quality:contact_success')
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
            return render(request, 'contact_us.html')
    
    return render(request, 'contact_us.html')

def contact_success(request):
    return render(request, 'contact_success.html')

# views.py


class GeneratePDFView(View):
    def get(self, request):
        # Get the last 10 readings from all stations
        recent_readings = AirQualityReading.objects.select_related('station').order_by('-timestamp')[:10]
        
        context = {
            'title': 'Air Quality Report',
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'chart_description': 'Historical AQI and PM2.5 Measurements',
            'data_source': 'Nairobi Air Quality Network',
            'recent_readings': recent_readings
        }
        
        template = get_template('report_template.html')
        html = template.render(context)
        
        # Create PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="air_quality_report.pdf"'
            return response
        
        return HttpResponse('Error generating PDF', status=500)