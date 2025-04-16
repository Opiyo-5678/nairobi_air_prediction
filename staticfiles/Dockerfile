# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

RUN pip install --upgrade pip
# Copy the requirements file to the working directory
COPY requirements.text .

# Install dependencies

RUN pip install --no-cache-dir -r requirements.text

# Copy the rest of the application code
COPY . .

# Expose the port your app runs on (default for Django is 8000)
EXPOSE 8000

# Command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]