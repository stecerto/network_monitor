from django.core.management.base import BaseCommand
from django.utils import timezone
import subprocess
from monitor.models import Device


class Command(BaseCommand):
    help = "Aggiorna lo stato dei dispositivi facendo ping"

    def handle(self, *args, **options):
        devices = Device.objects.all()
        for device in devices:
            result = subprocess.run(
                ["ping", "-c", "1", device.ip_address],
                stdout=subprocess.DEVNULL
            )

            device.status = "Online" if result.returncode == 0 else "Offline"
            device.last_check = timezone.now()
            device.save()
            self.stdout.write(f"{device.name} ({device.ip_address}) -> {device.status}")

