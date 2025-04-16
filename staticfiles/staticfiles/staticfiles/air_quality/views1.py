# import csv
# import os
# import joblib
# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.conf import settings
# import json

# # Correct Model Path
# #  @login_required
# # @login_required(login_url='/auth/login/')
# # def air_quality_view(request):
#     # Replace with your air quality logic
#     # return render(request, 'airquality/air_quality.html', {'data': 'Air quality data here'})

#     # return render(request, 'air_quality.html', context)
# MODEL_PATH = os.path.join(settings.BASE_DIR, "air_quality_model.pkl")

# # Load the model only once to improve performance


# def load_model():
#     try:
#         if not os.path.exists(MODEL_PATH):
#             print("Error: Model file not found at", MODEL_PATH)
#             return None
#         model = joblib.load(MODEL_PATH)
#         return model
#     except Exception as e:
#         print("Error loading model:", str(e))
#         return None

# # Air Quality Page

# @login_required(login_url='/auth/login/')
# def air_quality_page(request):
#     csv_file_path = os.path.join(settings.BASE_DIR, "locationa_names.csv") #Correct path
#     location_data = []

#     try:
#         with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 if row['location_name'].lower() == 'unknown':
#                     continue
#                 try:
#                     location_data.append({
#                         'name': row['location_name'],
#                         'lat': float(row['lat']),
#                         'lon': float(row['lon']),
#                     })
#                 except ValueError:
#                     print(f"Skipping row due to invalid lat/lon values: {row}")
#                     continue
#     except FileNotFoundError:
#         print(f"Error: CSV file not found at {csv_file_path}")
#         location_data = []

#     # Set initial map center (you can choose any valid location)
#     initial_lat = -1.286389  # Nairobi
#     initial_lon = 36.817223

#     context = {
#         'location_data': location_data,
#         'initial_lat': initial_lat,
#         'initial_lon': initial_lon,
#     }
#     return render(request, 'air_quality.html', context)
#   #  return render(request, 'air_quality.html', context)

  
#    # return redirect(f'auth/login/?next=/air-quality/')
# # API to predict air quality


# @csrf_exempt
# def predict_air_quality(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             lat = data.get('lat')
#             lon = data.get('lon')

#             if lat is None or lon is None:
#                 return JsonResponse({"error": "Latitude and longitude are required."}, status=400)

#             # Load trained model
#             model = load_model()
#             if model is None:
#                 return JsonResponse({"error": "Model failed to load. Check logs."}, status=500)

#             # Make prediction
#             try:
#                 prediction = model.predict([[lat, lon]])[0]
#             except Exception as e:
#                 return JsonResponse({"error": f"Prediction failed: {str(e)}"}, status=500)

#             # Get air quality level
#             air_quality_level, recommendations, alert = get_air_quality_info(prediction)

#             return JsonResponse({
#                 "prediction": prediction,
#                 "air_quality_level": air_quality_level,
#                 "recommendations": recommendations,
#                 "alert": alert
#             }, status=200)

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON request"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)

#     return JsonResponse({"error": "Invalid request method"}, status=405)

# # Function to categorize air quality level


# def get_air_quality_info(p2_value):
#     if p2_value <= 19:
#         return "Good", "Enjoy outdoor activities! Air quality is good.", "No alert"
#     elif 19.1 <= p2_value <= 35.4:
#         return "Moderate", "Reduce prolonged outdoor exercise if you are sensitive to pollution.", "Mild caution"
#     elif 35.5 <= p2_value <= 55.4:
#         return "Unhealthy for Sensitive Groups", "Wear a mask, close windows.", "Dangerous"
#     elif 55.5 <= p2_value <= 150.4:
#         return "Unhealthy", "Run an air purifier, limit outdoor activity. Wear a mask!.", "Very dangerous"
#     elif 150.5 <= p2_value <= 250.4:
#         return "Very Unhealthy", "Avoid outdoor activities, use air filters.", "Extremely dangerous"
#     else:
#         return "Hazardous", "Stay indoors, seek medical help if necessary.", "Emergency alert"