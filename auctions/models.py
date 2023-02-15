from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    photo = models.URLField(blank=True)
    maker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maker')
    time = models.DateTimeField(auto_now=True)
    
    cat_choices = [('Fashion','Fashion'),
    ('Home and Living', 'Home and Living'),
    ('Electronics and Vehicles', 'Electronics and Vehicles'),
    ('Toys and Hobbies', 'Toys and Hobbies'),
    ('Arts and Literature', 'Arts and Literature'),
    ('Music and Sports', 'Music and Sports'),
    ('Other Categories', 'Other Categories')]
    category = models.CharField(max_length=50, choices = cat_choices)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.title} ${self.price} {self.maker} {self.category} {self.time}'


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='item', default=None)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    bid = models.IntegerField(default=None)

    def __str__(self):
        return f"{self.bidder} {self.listing.title} ${self.bid}"
    

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='lsiting', default=None)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    comment = models.TextField(default=None)
    
    def __str__(self):
        return f'{self.comment} -{self.commenter}'

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    listings = models.ManyToManyField(Listing, default=None)
    
    
    def __Str__(self):
        return f'{self.user} {self.listings}'