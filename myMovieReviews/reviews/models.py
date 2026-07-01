from django.db import models


class Review(models.Model):
    GENRE_CHOICES = [
        ('action', '액션'),
        ('comedy', '코미디'),
        ('romance', '로맨스'),
        ('thriller', '스릴러'),
        ('horror', '공포'),
        ('sf', 'SF'),
        ('animation', '애니메이션'),
        ('drama', '드라마'),
        ('documentary', '다큐멘터리'),
    ]

    title = models.CharField(max_length=100)
    release_year = models.IntegerField()
    director = models.CharField(max_length=50)
    actor = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    rating = models.FloatField()
    running_time = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title