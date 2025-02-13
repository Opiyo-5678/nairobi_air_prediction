# from django.shortcuts import render

# Create your views here.
import googlemaps
from rest_framework.views import APIView
from rest_framework.response import Response

gmaps = googlemaps.Client(key='AIzaSyAgp3NnezwlY5Xe7AJvbmRJzdjNigTuZxU')


class HealthProvidersView(APIView):
    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        result = gmaps.places_nearby(location=(lat, lon), radius=5000, type='hospital')
        return Response(result)