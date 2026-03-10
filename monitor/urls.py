

from django.urls import path

from .views import device_list

urlpatterns = [
    path("", device_list, name="device_list"),
]