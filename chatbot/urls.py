from django.urls import path
from . import views

urlpatterns = [
    path("", views.chatbot_view, name="chatbot_view"),
    path("favorites/", views.favorites_view, name="favorites_view"),
    path("favorites/<int:favorite_id>/", views.delete_favorite, name="delete_favorite"),
    path("chat", views.chat_api, name="chat_api"),  
]
