from django.contrib import admin
from .models import User, Post

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("__str__", "post")
    filter_horizontal = ("likes",)

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")
    filter_horizontal = ("followings", "followers")
    

admin.site.register(Post, PostAdmin)
admin.site.register(User, UserAdmin)



