# # from django.db import models

# # Create your models here.
# from django.db import models

# class ChatbotMessage(models.Model):
#     user = models.CharField(max_length=255)  # Store user info (or use ForeignKey if needed)
#     message = models.TextField()  # Store the chatbot messages
#     response = models.TextField()  # Store chatbot's response
#     timestamp = models.DateTimeField(auto_now_add=True)  # Auto store time of message

#     def __str__(self):
#         return f"{self.user}: {self.message[:50]}"  # Show first 50 chars of message
