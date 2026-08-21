from django.urls import path

from . import views

app_name = "block_data_table_customers"

urlpatterns = [
    path("", views.index, name="index"),
    path("update/<int:pk>/", views.update, name="update"),
    path("delete/<int:pk>/", views.delete, name="delete"),
    path("bulk-delete/", views.bulk_delete, name="bulk_delete"),
]
