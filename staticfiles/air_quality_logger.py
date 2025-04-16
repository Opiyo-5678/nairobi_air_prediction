import requests
import csv
from datetime import datetime
import time
import os

# Your WAQI API token
api_token = "8d7134bd47dfec19a3a6120c52d3906e7da3e30b"

# WAQI API endpoint for Nairobi
city = "Nairobi"
url = f"https://api.waqi.info/feed/{city}/?token={api_token}"

# Path to the CSV file in the Django static folder
csv_file = os.path.join(os.path.dirname(__file__), "static", "air_quality_data.csv")

# Function to fetch and log data


def fetch_and_log_data():
    # Make the API request
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'ok':
            # Extract air quality data
            aqi = data['data']['aqi']
            pm25 = data['data']['iaqi']['pm25']['v'] if 'pm25' in data['data']['iaqi'] else None
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log data to CSV file
            with open(csv_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                # Write header if the file is empty
                if file.tell() == 0:
                    writer.writerow(["Timestamp", "AQI", "PM2.5"])
                writer.writerow([timestamp, aqi, pm25])
            
            print(f"Data logged: {timestamp}, AQI: {aqi}, PM2.5: {pm25}")
        else:
            print("Error in API response:", data['data'])
    else:
        print("Failed to fetch data. Status code:", response.status_code)

# Automate data fetching and logging


while True:
    fetch_and_log_data()
    # Wait for 1 hour (3600 seconds) before fetching again
    time.sleep(3600)