from django.urls import path

from . import views

app_name = "block_dashboard_overview"

urlpatterns = [
    path("", views.index, name="index"),
    path("cash-stream/", views.cash_stream, name="cash_stream"),
]
