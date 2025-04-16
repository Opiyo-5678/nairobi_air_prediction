import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from .models import AirQualityStation, AirQualityReading

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

# @login_required(login_url='/auth/login/')
# def get_air_quality_data(request):
#     """API endpoint to fetch air quality data for all stations"""
#     api_key = "8d7134bd47dfec19a3a6120c52d3906e7da3e30b"  # Your WAQI API key
    
#     air_quality_data = []
    
      
#     # Make sure all stations exist in the database
#     for station_info in NAIROBI_STATIONS:
#         station, created = AirQualityStation.objects.get_or_create(
#             name=station_info['name'],
#             defaults={
#                 'latitude': station_info['lat'],
#                 'longitude': station_info['lon']
#             }
#         )
        
#         # Use geo coordinates to get nearest station data
#         api_url = f"https://api.waqi.info/feed/geo:{station_info['lat']};{station_info['lon']}/"
        
#         try:
#             response = requests.get(f"{api_url}?token={api_key}")
            
#             if response.status_code == 200:
#                 data = response.json()
#                 if data['status'] == 'ok':
#                     # Some stations might not have all data fields
#                     # Use get() with default values to handle missing data
#                     station_data = {
#                         'name': station_info['name'],
#                         'aqi': data['data'].get('aqi', 'N/A'),
#                         'latitude': station_info['lat'],
#                         'longitude': station_info['lon'],
#                         'dominant_pollutant': data['data'].get('dominentpol', 'N/A'),
#                         'timestamp': data['data'].get('time', {}).get('s', 'N/A'),
#                     }
                    
#                     # Extract pollutant details if available
#                     pollutants = {}
#                     if 'iaqi' in data['data']:
#                         for pollutant, value in data['data']['iaqi'].items():
#                             if 'v' in value:
#                                 pollutants[pollutant] = value['v']
#                         station_data['pollutants'] = pollutants
                    
#                     air_quality_data.append(station_data)
                    
#                     # Convert timestamp string to datetime object
#                     try:
#                         if station_data['timestamp'] != 'N/A':
#                             # Parse the timestamp format from the API
#                             timestamp = datetime.strptime(station_data['timestamp'], '%Y-%m-%d %H:%M:%S')
#                         else:
#                             # Use current time if no timestamp is provided
#                             timestamp = timezone.now()
                            
#                         # Store reading in database
#                         reading, created = AirQualityReading.objects.get_or_create(
#                             station=station,
#                             timestamp=timestamp,
#                             defaults={
#                                 'aqi': None if station_data['aqi'] == 'N/A' else station_data['aqi'],
#                                 'dominant_pollutant': station_data['dominant_pollutant'],
#                                 'pm25': pollutants.get('pm25'),
#                                 'pm10': pollutants.get('pm10'),
#                                 'o3': pollutants.get('o3'),
#                                 'no2': pollutants.get('no2'),
#                                 'so2': pollutants.get('so2'),
#                                 'co': pollutants.get('co'),
#                                 'humidity': pollutants.get('h'),
#                                 'temperature': pollutants.get('t'),
#                                 'pressure': pollutants.get('p'),
#                                 'wind': pollutants.get('w')
#                             }
#                         )
                        
#                         if not created:
#                             # Update existing reading if needed
#                             reading.aqi = None if station_data['aqi'] == 'N/A' else station_data['aqi']
#                             reading.dominant_pollutant = station_data['dominant_pollutant']
#                             reading.pm25 = pollutants.get('pm25')
#                             reading.pm10 = pollutants.get('pm10')
#                             reading.o3 = pollutants.get('o3')
#                             reading.no2 = pollutants.get('no2')
#                             reading.so2 = pollutants.get('so2')
#                             reading.co = pollutants.get('co')
#                             reading.humidity = pollutants.get('h')
#                             reading.temperature = pollutants.get('t')
#                             reading.pressure = pollutants.get('p')
#                             reading.wind = pollutants.get('w')
#                             reading.save()
                            
#                     except Exception as e:
#                         print(f"Error saving reading to database: {str(e)}")
            
#         except Exception as e:
#             # In production, you would log this error
#             print(f"Error fetching data for {station_info['name']}: {str(e)}")
#             # Add a placeholder with error info
#             air_quality_data.append({
#                 'name': station_info['name'],
#                 'aqi': 'Error',
#                 'latitude': station_info['lat'],
#                 'longitude': station_info['lon'],
#                 'error': str(e)
#             })
    
#     return JsonResponse({'air_quality_data': air_quality_data})

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
                        'dominant_pollutant': 'pm25',  # Override dominant pollutant to PM2.5
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
                                'pm25': pollutants.get('pm25'),
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
                            reading.pm25 = pollutants.get('pm25')
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
    return render(request, 'historical_data.html')