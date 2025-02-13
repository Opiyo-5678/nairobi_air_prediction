from django.shortcuts import render

# Create your views here.
import joblib
from rest_framework.views import APIView
from rest_framework.response import Response

model = joblib.load('C:\\Users\\ADMIN PC\\air_quality_project\\air_quality_model (2).pkl')


class AirQualityView(APIView):
    def post(self, request):
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        prediction = model.predict([[lat, lon]])
        return Response({'prediction': prediction[0]})