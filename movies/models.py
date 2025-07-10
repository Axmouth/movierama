from django.db import models
from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING

User = get_user_model()

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')

    def __str__(self) -> str:
        return str(self.title)

class Vote(models.Model):
    LIKE = 'like'
    HATE = 'hate'
    VOTE_TYPES = [
        (LIKE, 'Like'),
        (HATE, 'Hate'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPES)

    class Meta:
        unique_together = ('user', 'movie')
