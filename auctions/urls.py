from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing', views.create_listing, name='create_listing'),
    path('listings/<int:listing_id>', views.listing, name='listing'),
    path('listings/<int:listing_id>/close_auction', views.close_auction, name='close_auction'),
    path('categories/<str:category>', views.categories, name='categories'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('watchlist/add_remove/<int:listing_id>',  views.add_remove_watchlist, name='add_remove_watchlist'),
    path('maker/<int:maker_id>', views.maker, name="maker")
]
