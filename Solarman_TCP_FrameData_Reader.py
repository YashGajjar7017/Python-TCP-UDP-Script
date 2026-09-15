import socket
import sys
from pysolarmanv5 import PySolarmanV5

# --- CONFIGURATION ---
TARGET_IP = "192.168.88.150"  # Replace with actual Wi-Fi Logger IP
LOGGER_SN = 1234567890  # Replace with Wi-Fi Logger Serial Number
PORTS_TO_CHECK = [8899, 8889, 502, 80, 500]


def check_open_ports(ip, ports):
    """Scans TCP ports to verify which services are listening."""
    print(f"--- 1. SCANNING PORTS ON {ip} ---")
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)  # Fast timeout check
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"[+] TCP Port {port}: OPEN / LISTENING")
            open_ports.append(port)
        else:
            print(f"[-] TCP Port {port}: CLOSED / BLOCKED (Error Code: {result})")
        sock.close()
    return open_ports


def capture_solarman_frame(ip, sn, port):
    """Establishes Solarman V5 connection and captures raw byte frames."""
    print(f"\n--- 2. ESTABLISHING SOLARMAN V5 CONNECTION (Port {port}) ---")
    try:
        # Initialize PySolarmanV5 Client
        modbus = PySolarmanV5(
            address=ip, serial=sn, port=port, mb_slave_id=1, verbose=True
        )

        # Build raw Modbus RTU Read Request: Read 2 holding registers starting at 31001 (0x7919)
        modbus_req = bytearray([0x01, 0x03, 0x79, 0x19, 0x00, 0x02])

        # Append calculated Modbus CRC16
        crc = modbus._calc_crc(modbus_req)
        modbus_req.extend(crc.to_bytes(2, byteorder="little"))

        print("\n--- 3. FRAME CAPTURE ---")
        print(f"[+] Raw Modbus RTU Payload: {modbus_req.hex(' ')}")

        # Encode inside Solarman V5 Header / Trailer (0xA5 ... 0x15)
        v5_sent_frame = modbus._v5_frame_encoder(modbus_req)
        print(
            f"[+] Full Solarman V5 Sent Frame  : {v5_sent_frame.hex(' ')}"
        )

        # Transmit frame over TCP and read raw byte response
        v5_received_frame = modbus._send_receive(v5_sent_frame)
        print(
            f"[+] Full Solarman V5 Recv Frame  : {v5_received_frame.hex(' ')}"
        )

        # Decode response payload
        modbus_reply = modbus._v5_frame_decoder(v5_received_frame)
        print(
            f"[+] Extracted Modbus RTU Response: {modbus_reply.hex(' ')}"
        )

    except Exception as e:
        print(f"\n[!] Frame capture failed: {e}")


# --- EXECUTION ---
if __name__ == "__main__":
    open_ports = check_open_ports(TARGET_IP, PORTS_TO_CHECK)

    if 8899 in open_ports:
        capture_solarman_frame(TARGET_IP, LOGGER_SN, port=8899)
    elif open_ports:
        print(
            f"\n[!] Port 8899 is closed, but open ports found: {open_ports}. Attempting capture on {open_ports[0]}..."
        )
        capture_solarman_frame(TARGET_IP, LOGGER_SN, port=open_ports[0])
    else:
        print(
            "\n[!] Connection Aborted: No open TCP ports detected on this IP. Double-check device IP address."
        )