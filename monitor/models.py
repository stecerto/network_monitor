from django.db import models


class Device(models.Model):
    name = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    vendor = models.CharField(max_length=200, blank=True)
    status = models.BooleanField(default=False)
    last_check = models.DateTimeField()
    os = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

