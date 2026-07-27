from django.urls import path

from . import views

app_name = "block_auth_split_brand"

urlpatterns = [
    path("", views.index, name="index"),
    path("validate/", views.validate, name="validate"),
    path("submit/", views.submit, name="submit"),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("sign-up/validate/", views.sign_up_validate, name="sign_up_validate"),
    path("sign-up/submit/", views.sign_up_submit, name="sign_up_submit"),
]
