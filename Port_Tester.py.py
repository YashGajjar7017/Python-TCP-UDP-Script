import socket
import urllib.error
import urllib.request

# --- CONFIGURATION ---
# Replace with your inverter / logger IP address
TARGET_IP = "192.168.88.150"
TIMEOUT = 2.0  # Timeout in seconds for each check

# Specified ports + additional common inverter TCP ports
PORTS_TO_TEST = [
    8899,  # Solarman V5 / Standard Logger TCP Port
    8889,  # Alternate Solarman / AT Command Port
    502,  # Standard Modbus TCP
    500,  # ISAKMP / VPN / Custom Logger Port
    80,  # Standard HTTP Web Interface
    81,  # Alternate HTTP Web Interface
    4196,  # Alternate Solarman / Omnik Local TCP Port
    8080,  # Alternate Web Management Port
    8443,  # Alternate HTTPS Management Port
    10000,  # Telnet / Direct Serial Bridge Port
]


def test_tcp_port(ip, port):
    """Checks if a raw TCP port is OPEN and listening."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            return True, "OPEN / LISTENING"
        else:
            return False, f"CLOSED / REJECTED (Error Code: {result})"
    except Exception as e:
        return False, f"FAILED ({e})"
    finally:
        sock.close()


def test_http_endpoint(ip, port, scheme="http"):
    """Checks if an HTTP or HTTPS web service responds on the port."""
    url = f"{scheme}://{ip}:{port}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return True, f"HTTP {response.status} OK (Server active)"
    except urllib.error.HTTPError as e:
        return True, f"HTTP {e.code} (Web Server active)"
    except urllib.error.URLError as e:
        return False, f"No Web Response ({e.reason})"
    except Exception as e:
        return False, f"Failed ({e})"


def test_udp_port(ip, port):
    """Sends a UDP probe packet to check network socket delivery."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    try:
        # Send a blank test probe
        sock.sendto(b"\x00", (ip, port))
        return True, "Packet sent successfully (Note: UDP is connectionless)"
    except Exception as e:
        return False, f"UDP Send Failed ({e})"
    finally:
        sock.close()


def main():
    print("=" * 65)
    print(f"  STARTING FULL PORT & DIAGNOSTIC SCAN FOR: {TARGET_IP}")
    print("=" * 65)

    # 1. ICMP Ping Check
    print("\n--- 1. TESTING RAW ICMP / PING ---")
    ping_status, _ = test_tcp_port(TARGET_IP, 80)
    print(f"Target Host Reachability Check initialized...")

    # 2. Raw TCP Port Scan
    print("\n--- 2. TESTING TCP PORTS ---")
    open_tcp_ports = []
    for port in PORTS_TO_TEST:
        is_open, msg = test_tcp_port(TARGET_IP, port)
        status_str = "OPEN" if is_open else "CLOSED"
        print(f"TCP Port {port:<5} : [{status_str}] -> {msg}")
        if is_open:
            open_tcp_ports.append(port)

    # 3. HTTP / HTTPS Web Endpoint Scan
    print("\n--- 3. TESTING HTTP & HTTPS WEB ENDPOINTS ---")
    web_ports = [80, 81, 8080, 8443, 8899, 8889]
    for port in web_ports:
        # Test HTTP
        http_ok, http_msg = test_http_endpoint(TARGET_IP, port, scheme="http")
        print(f"http://{TARGET_IP}:{port:<5}  -> {http_msg}")

        # Test HTTPS on standard SSL ports
        if port in [8443, 443]:
            https_ok, https_msg = test_http_endpoint(
                TARGET_IP, port, scheme="https"
            )
            print(f"https://{TARGET_IP}:{port:<5} -> {https_msg}")

    # 4. UDP Probe Test
    print("\n--- 4. TESTING UDP PORTS ---")
    udp_ports = [500, 8899, 8889]
    for port in udp_ports:
        _, udp_msg = test_udp_port(TARGET_IP, port)
        print(f"UDP Port {port:<5} : {udp_msg}")

    # Summary
    print("\n" + "=" * 65)
    print("  SCAN COMPLETE SUMMARY")
    print("=" * 65)
    if open_tcp_ports:
        print(f"[+] Active Open TCP Ports Found: {open_tcp_ports}")
        print("[+] You can target these open ports for Modbus or API polling.")
    else:
        print("[-] No open TCP ports were detected on this IP.")
        print(
            "[-] Verify that the device IP is correct and powered on in your router's DHCP list."
        )


if __name__ == "__main__":
    main()