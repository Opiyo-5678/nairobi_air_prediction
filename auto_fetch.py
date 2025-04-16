import os
import sys
import schedule
import time
from datetime import datetime

# Set up Django environment
project_path = r"C:\Users\ADMIN PC\air_quality_project"
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality.settings')

import django
django.setup()

from django.core.management import call_command

LOG_FILE = os.path.join(project_path, "auto_fetch.log")

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def fetch_job():
    log("Starting air quality fetch...")
    try:
        call_command('fetch_air_quality')
        log("Fetch completed successfully")
    except Exception as e:
        log(f"Failed: {str(e)}")

# Schedule hourly job
schedule.every().hour.at(":00").do(fetch_job)

log("Scheduler started")
while True:
    schedule.run_pending()
    time.sleep(1)