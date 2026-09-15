import asyncio
import socket

TARGET_IP = "192.168.88.88"  # Logger IP address
CONCURRENCY_LIMIT = 500      # Number of parallel tasks
TIMEOUT = 0.8                # Timeout per port (seconds)

# Ports to probe specifically for HTTP/HTTPS responses
HTTP_PORTS = {80, 8080, 8888, 8000, 443, 8443}

async def check_tcp_port(semaphore, ip, port):
    """Attempt an asynchronous TCP connection and check for HTTP headers."""
    async with semaphore:
        try:
            conn = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(conn, timeout=TIMEOUT)
            
            result_str = f"[+] TCP Port {port:<5} : OPEN"
            
            # If it's a common web port, send a lightweight HTTP GET request
            if port in HTTP_PORTS:
                writer.write(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                await writer.drain()
                try:
                    data = await asyncio.wait_for(reader.read(100), timeout=0.5)
                    if b"HTTP" in data:
                        result_str += " (HTTP Service Detected)"
                except Exception:
                    pass
            
            writer.close()
            await writer.wait_closed()
            print(result_str)
            return port
        except Exception:
            return None

async def check_udp_port(semaphore, ip, port):
    """Probe UDP port with a zero-byte datagram."""
    async with semaphore:
        loop = asyncio.get_running_loop()
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(TIMEOUT)
            
            # Send a broadcast/ping payload
            sock.sendto(b"\x00", (ip, port))
            
            # Non-blocking receive attempt
            sock.setblocking(False)
            await loop.sock_recv(sock, 1024)
            print(f"[+] UDP Port {port:<5} : OPEN / RESPONDING")
            sock.close()
            return port
        except Exception:
            return None

async def main():
    print(f"Starting Fast Multi-Protocol Scan on {TARGET_IP}...")
    print(f"Testing TCP & UDP Ports 1 to 65535 (Concurrency: {CONCURRENCY_LIMIT})\n" + "=" * 55)
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    # 1. TCP Scan
    print("--- Scanning TCP Protocols (TCP / HTTP / HTTPS / Modbus) ---")
    tcp_tasks = [check_tcp_port(semaphore, TARGET_IP, port) for port in range(1, 65536)]
    tcp_results = await asyncio.gather(*tcp_tasks)
    open_tcp = [p for p in tcp_results if p is not None]

    # 2. Key UDP Scan (Focusing on common configuration UDP ports)
    print("\n--- Scanning High-Priority UDP Ports ---")
    common_udp_ports = [161, 53, 67, 68, 500, 1900, 5353, 10001, 48899, 58899, 8899]
    udp_tasks = [check_udp_port(semaphore, TARGET_IP, port) for port in common_udp_ports]
    udp_results = await asyncio.gather(*udp_tasks)
    open_udp = [p for p in udp_results if p is not None]

    print("\n" + "=" * 55)
    print(f"Scan Finished.")
    print(f"Open TCP Ports: {open_tcp if open_tcp else 'None'}")
    print(f"Open UDP Ports: {open_udp if open_udp else 'None'}")

if __name__ == "__main__":
    # Windows-specific event loop policy for high socket concurrency
    if hasattr(asyncio, 'set_event_loop_policy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())