from django.urls import path
from .views import analyze_view, analyze_vk_view

urlpatterns = [
    path('analyze/', analyze_view, name='analyze'),  # Убедитесь, что здесь указано имя 'analyze'
    path('analyze_vk/', analyze_vk_view, name='analyze_vk'),
]
