import subprocess
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.shortcuts import render
from django.utils import timezone
from .models import Device
from mac_vendor_lookup import MacLookup
from scapy.all import ARP, Ether, srp

mac_lookup = MacLookup()

def get_vendor(mac):
    try:
        return MacLookup().lookup(mac)
    except:
        return "Unknown"

# Funzione per controllare un singolo IP
def check_device(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],  # Timeout 1s
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    if result.returncode == 0:
        hostname = "Unknown"
        try:  # reserve DNS
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            pass

        #prova hostname locale
        if hostname == "unknown":
            if vendor != "Unknown":
                hostname = f"{vendor} device"
            elif mac:
                hostname = f"Device-{mac[:8]}"

            try:
                hostname = socket.getfqdn(ip)
            except:
                pass

        return ip, hostname, "Online"

    return ip, None, "Offline"



def device_list(request):
    base_ip = request.GET.get("ip", "192.168.1.1")
    network = ".".join(base_ip.split(".")[:3])
    ips = [f"{network}.{i}" for i in range(1, 255)]



    online_devices = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_device, ip) for ip in ips]
        for future in as_completed(futures):
            ip, hostname, status = future.result()
            if status == "Online":
                # Salviamo solo gli online nel DB

                mac = get_mac(ip)

                if mac:
                    vendor = get_vendor(mac)
                else:
                    vendor = "Unknown"

                if hostname is None:
                    hostname = "Unknown"
                device, created = Device.objects.get_or_create(
                    ip_address=ip,
                    defaults={
                        "name": hostname,
                        "mac_address": mac,
                        "vendor": vendor,
                        "status": status,
                        "last_check": timezone.now()
                    }
                )
                if not created:
                    device.name = hostname or "Unknown"
                    device.mac_address = mac
                    device.vendor = vendor
                    device.status = status
                    device.last_check = timezone.now()
                    device.save()
                online_devices.append(device)

                total_devices = Device.objects.count()
                online_count = Device.objects.filter(status="Online").count()
                offline_count = Device.objects.filter(status="Offline").count()

    # Passiamo solo i dispositivi online al template
    return render(request, "monitor/device_list.html", {
        "devices": online_devices,
        "total_devices": total_devices,
        "online_count": online_count,
        "offline_count": offline_count
    })

def get_mac(ip):
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = broadcast / arp_request

    result = srp(packet, timeout=1, verbose=0)[0]

    if result:
        return result[0][1].hwsrc
    return None

