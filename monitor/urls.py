from os import name

from django.urls import path
from . import views

from .views import device_list, port_scan

urlpatterns = [
    path("", views.device_list, name="device_list"),
    path("device/table/", views.device_table, name="device_table"),
    path("device/<int:device_id>/", views.device_detail, name="device_detail"),
    path("api/scan-ports/<str:ip>/", port_scan, name="port_scan"),
    path("send/<str:ip>/<int:port>/", views.send_message, name="send_message"),
]