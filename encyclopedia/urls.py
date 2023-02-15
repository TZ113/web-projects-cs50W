from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>/", views.entry_page, name="entry_page"),
    path("search/", views.search, name="search"),
    path("create_page/", views.create_page, name="create_page"),
    path("edit_page/<str:title>/", views.edit_page, name="edit_page"),
    path("save_page/", views.save_edited_page, name="save_edited_page"),
    path("random_page/", views.rnd_page, name="rnd_page")
]
