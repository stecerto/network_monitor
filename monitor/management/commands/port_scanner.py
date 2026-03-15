import nmap

def scan_ports(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments="-F")
    ports = []

    for proto in nm[ip].all_protocols():
        lport = nm[ip][proto].keys()

        for port in lport:
            ports.append({
                "port": port,
                "state": nm[ip][proto][port]["state"]
            })

    return ports