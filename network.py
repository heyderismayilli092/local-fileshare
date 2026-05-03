import fcntl
import struct
import psutil

# get ip address
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24]
    )

# find active interface
def find_active_interface():  # Finds the active interface on the device
    # All active interfaces are retrieved
    interfaces = psutil.net_if_addrs()
    candidates = list(interfaces.keys())
    # Network interfaces are purchased (Wi-Fi and Ethernet)
    wifi_candidates = [i for i in candidates if i.startswith(("wlo", "wlan", "wlp"))]
    eth_candidates = [i for i in candidates if i.startswith(("eth", "eno", "enp"))]
    # Filters those with active IP addresses
    def get_valid_ip(ifname):
        for addr in interfaces.get(ifname, []):
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                return addr.address
        return None
    # Wi-Fi check
    for ifname in wifi_candidates:
        ip = get_valid_ip(ifname)
        if ip:
            return ifname, ip
    # Ethernet check
    for ifname in eth_candidates:
        ip = get_valid_ip(ifname)
        if ip:
            return ifname, ip
    # Works over localhost if there is no connection
    return "lo", "127.0.0.1"

