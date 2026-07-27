from django.urls import path

from . import views

app_name = "block_wizard_onboarding"

urlpatterns = [
    path("", views.index, name="index"),
    path("validate/", views.validate, name="validate"),
    path("next/", views.next_step, name="next"),
    path("prev/", views.prev_step, name="prev"),
    path("submit/", views.submit, name="submit"),
]
