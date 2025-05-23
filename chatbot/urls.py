from django.urls import path
from .views import chatbot_view, favorites_view, delete_favorite

urlpatterns = [
    path('', chatbot_view, name='chatbot'),
    path('favorites/', favorites_view, name='favorites_view'),  # GET + POST
    path('favorites/<int:favorite_id>/', delete_favorite, name='delete_favorite'),  # DELETE
]
