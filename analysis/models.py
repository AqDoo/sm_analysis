from django.db import models

# Create your models here.
# analysis/models.py
from django.db import models


class RedditPost(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()  # Это поле для хранения ссылки на пост
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()

    def __str__(self):
        return self.title

class YouTubeVideo(models.Model):
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=255)
    published_at = models.DateTimeField(auto_now_add=True)
