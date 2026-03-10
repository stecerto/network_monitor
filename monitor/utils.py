import subprocess




def ping_device(ip):
    result = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.DEVNULL)
    return result.returncode == 0
