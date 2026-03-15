import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

import paramiko
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from mac_vendor_lookup import MacLookup
from rest_framework.decorators import api_view
from rest_framework.response import Response
from scapy.all import ARP, Ether
from rest_framework.decorators import api_view
from rest_framework.response import Response
from monitor.management.commands.network import scan_ports_with_service
import socket
from django.http import JsonResponse

from monitor.management.commands.port_scanner import scan_ports
from .models import Device
import re

mac_lookup = MacLookup()

#-- Utility Functions --
def get_vendor(mac):
    try:
        return MacLookup().lookup(mac)
    except:
        return "Unknown"


def get_mac(ip):
    result = subprocess.run(["arp", "-n", ip], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    # regex per MAC address
    match = re.search(r"([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})", result.stdout)
    if match:
        return match.group(0)
    return None

def detect_os(ip):
    """
    Rilevamento OS molto semplice basato su TTL.
    Windows: TTL ~128
    Linux/Unix: TTL ~64
    Router: TTL ~255
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True,
            text=True
        )
        ttl_match = re.search(r"ttl=(\d+)", result.stdout)
        if ttl_match:
            ttl = int(ttl_match.group(1))
            if ttl >= 128:
                return "Windows"
            elif ttl >= 64:
                return "Linux/Unix"
            elif ttl >= 255:
                return "Router"
            else:
                return "Unknown"
    except:
        pass
    return "Unknown"

def check_device(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        return ip, "Unknown", None,  "Unknown", False, "Unknown"  # offline

    # online, recuperiamo mac e vendor
    mac = get_mac(ip)
    vendor = get_vendor(mac) if mac else "Unknown"

    try:
        name = socket.gethostbyaddr(ip)[0]
    except:
        name = f"{vendor} device" if vendor != "Unknown" else f"Device-{ip.split('.')[-1]}"

    os_type = detect_os(ip)


    return ip, name, mac, vendor, True, os_type


def device_list(request):
    base_ip = request.GET.get("ip", "192.168.1.1")
    network = ".".join(base_ip.split(".")[:3])
    ips = [f"{network}.{i}" for i in range(1, 255)]

    online_devices = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_device, ip) for ip in ips]
        for future in as_completed(futures):
            ip, name, mac, vendor, status, os_type = future.result()
            if status:
                device, created = Device.objects.get_or_create(
                    ip_address=ip,
                    defaults={
                        "name": name,
                        "mac_address": mac,
                        "vendor": vendor,
                        "status": status,
                        "last_check": timezone.now(),
                        "os": os_type
                    }
                )
                if not created:
                    device.name = name or "Unknown"
                    device.mac_address = mac
                    device.vendor = vendor
                    device.status = status
                    device.last_check = timezone.now()
                    device.os = os_type
                    device.save()

                online_devices.append(device)

    total_devices = Device.objects.count()
    online_count = Device.objects.filter(status=True).count()
    offline_count = Device.objects.filter(status=False).count()

    return render(request, "monitor/device_list.html", {
        "devices": online_devices,
        "total_devices": total_devices,
        "online_count": online_count,
        "offline_count": offline_count,
        "current_ip": base_ip
    })

def device_table(request):
    devices = Device.objects.all()
    return render( request, "monitor/device_table.html", {"devices": devices} )


def device_detail(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    return render(request, "monitor/device_detail.html", {"device": device})

def get_memory(ip, user, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=user, password=password)
    stdin, stdout, stderr = ssh.exec_command("free -h")
    memory = stdout.read().decode()
    ssh.close()
    return memory



def send_message(request, ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)

        s.connect((ip, int(port)))

        message = f"GET / HTTP/1.1\r\nHost: {ip}\r\n\r\n"
        s.send(message.encode())

        response = b""

        while True:
            try:
                chunk = s.recv(1024)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break

        s.close()
        response_text = response.decode(errors="ignore")

        # prendiamo solo gli header HTTP
        headers = response_text.split("\r\n\r\n")[0]

        banner = "Unknown service"

        for line in headers.split("\r\n"):
            if line.lower().startswith("server:"):
                banner = line
                break

        return JsonResponse({
            "status": "ok",
            "banner": banner
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })

@api_view(['GET'])
def port_scan(request, ip):
    ports = scan_ports_with_service(ip)
    return Response({
        "ip": ip,
        "ports": ports
    })


'''  
def get_mac(ip):
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = broadcast / arp_request

    result = srp(packet, timeout=1, verbose=0)[0]

    if result:
        return result[0][1].hwsrc
    return None
'''