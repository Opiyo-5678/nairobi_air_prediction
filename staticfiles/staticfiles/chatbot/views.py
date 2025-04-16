# from django.shortcuts import render

# Create your views here.
import openai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

openai.api_key = settings.OPENAI_API_KEY


class ChatbotView(APIView):
    def post(self, request):
        user_message = request.data.get('message')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        return Response({'response': response['choices'][0]['message']['content']})