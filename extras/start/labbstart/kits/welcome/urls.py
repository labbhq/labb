from django.urls import path

from labb.shortcuts import set_theme_view

from . import views

app_name = "__LABBSTART_APP_NAME__"

urlpatterns = [
    path("", views.index, name="index"),
    path("set-theme/", set_theme_view, name="set_theme"),
]
