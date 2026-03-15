import nmap

def scan_ports_with_service(ip):
    nm = nmap.PortScanner()

    try:
        # scansione TCP più comune: prime 1024 porte
        nm.scan(ip, '22,80,443,3306,8080') #'1-1024')

        result = []

        # nmap restituisce un dict con i protocolli
        for proto in nm[ip].all_protocols():
            ports = nm[ip][proto].keys()
            for port in sorted(ports):
                service = nm[ip][proto][port]['name']  # nome del servizio
                result.append({
                    "port": port,
                    "protocol": proto,
                    "service": service
                })
        return result

    except Exception as e:
        return [{"error": str(e)}]