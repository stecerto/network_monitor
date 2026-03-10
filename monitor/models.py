from django.db import models


class Device(models.Model):
    name = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    vendor = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20)
    last_check = models.DateTimeField()

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

