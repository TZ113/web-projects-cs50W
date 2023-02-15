from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followings = models.ManyToManyField('self', symmetrical=False, related_name='user_follows', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True)


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poster")
    post = models.TextField()
    time = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='likers', blank=True)
    
    def __str__(self):
        return f"{self.poster} at {self.time} posted:- {self.post} | currently having {self.likes.all().count()} likes"
    
    
    