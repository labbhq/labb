from django.urls import path

from . import views

app_name = "block_settings_workspace"

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/validate/", views.profile_validate, name="profile_validate"),
    path("profile/save/", views.profile_save, name="profile_save"),
    path("team/validate/", views.invite_validate, name="invite_validate"),
    path("team/invite/", views.invite_save, name="invite_save"),
    path("billing/plan/<int:pk>/", views.plan_change, name="plan_change"),
]
