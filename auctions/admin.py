from django.contrib import admin
from .models import *


class ListingAdmin(admin.ModelAdmin):
    list_display = ("__str__", "maker")

class BidAdmin(admin.ModelAdmin):
    list_display = ("__str__", "bid")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "commenter")

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ('listings', )
    

admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist, WatchlistAdmin)