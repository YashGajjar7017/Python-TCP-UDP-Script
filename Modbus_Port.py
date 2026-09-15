import socket

# Target settings
TARGET_IP = "192.168.88.100"  # Replace with your logger's IP address
PORTS_TO_SCAN = [502, 8899, 80, 8080, 4897]  # Common Modbus and Web ports
TIMEOUT = 2.0  # Time in seconds to wait for a response

def scan_port(ip, port):
    """Attempt to establish a TCP socket connection to a specific port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    
    result = sock.connect_ex((ip, port))
    sock.close()
    
    # connect_ex returns 0 if the connection was successful
    return result == 0

def run_port_scan():
    print(f"Scanning target IP: {TARGET_IP}...\n" + "-" * 35)
    
    for port in PORTS_TO_SCAN:
        is_open = scan_port(TARGET_IP, port)
        if is_open:
            print(f"[+] Port {port:<5} : OPEN")
        else:
            print(f"[-] Port {port:<5} : Closed or Blocked")

if __name__ == "__main__":
    run_port_scan()