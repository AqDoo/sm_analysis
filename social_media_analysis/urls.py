# social_media_analysis/urls.py
from django.contrib import admin
from django.urls import path, include  # Не забудьте импортировать include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analyze/', include('analysis.urls')),  # Убедитесь, что путь включает ваше приложение
]
