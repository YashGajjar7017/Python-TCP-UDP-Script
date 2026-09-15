import socket
import time

# Targeted UDP Discovery for Solar Wi-Fi Loggers
UDP_IP = "255.255.255.255"  # Broadcast IP
UDP_PORTS = [48899, 10001, 58899, 8899]
DISCOVERY_MSG = b"HF-A11ASSISTHREAD"  # Standard logger wakeup command

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.settimeout(2.0)

print("Sending UDP Wakeup Broadcasts...\n" + "=" * 40)

for port in UDP_PORTS:
    print(f"Testing UDP Port {port}...")
    try:
        sock.sendto(DISCOVERY_MSG, (UDP_IP, port))
        data, addr = sock.recvfrom(1024)
        print(f"\n[+] SUCCESS! Response received from Logger at {addr[0]}:{addr[1]}")
        print(f"    Raw Response Data: {data.decode('utf-8', errors='ignore')}\n")
    except socket.timeout:
        print(f"    [-] No reply on UDP port {port}")

sock.close()