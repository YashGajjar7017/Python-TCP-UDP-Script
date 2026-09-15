import socket
import time

# --- CONFIGURATION ---
LOGGER_IP = "192.168.88.88"  # Update to your logger's actual IP address
LOGGER_PORT = 54188          # Default Solarman/Logger TCP port
TIMEOUT = 5.0                # Connection timeout in seconds

def hex_format(data_bytes):
    """Formats raw binary bytes into readable space-separated HEX string."""
    return ' '.join(f'{b:02X}' for b in data_bytes)

def read_device_frames_as_client(ip, port):
    """Connects to the logger as a client, sends a raw query, and reads incoming frames."""
    print(f"\n--- ATTEMPTING CLIENT CONNECTION TO {ip}:{port} ---")
    
    # 1. Raw Modbus RTU Frame embedded in Solarman V5 Wrapper (Read Registers 31001-31002)
    # Starts with 0xA5 (Solarman Header), contains target query, ends with 0x15
    # Replace the serial number bytes if your logger requires specific header validation
    raw_request_frame = bytearray([
        0xA5, 0x17, 0x00, 0x10, 0x45, 0x00, 0x00, 0x00,  # Header & Sequence
        0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00,  # Protocol payload
        0x01, 0x03, 0x79, 0x19, 0x00, 0x02, 0x9D, 0x59,  # Modbus RTU Command + CRC
        0x00, 0x15                                      # Trailer
    ])

    try:
        # Create TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TIMEOUT)
        client_socket.connect((ip, port))
        
        print(f"[+] TCP Connection Established to {ip}:{port}")
        
        # Display Sent Request Frame
        print(f"\n[OUTGOING REQUEST FRAME] ({len(raw_request_frame)} bytes):")
        print(f"HEX: {hex_format(raw_request_frame)}")

        # Send frame
        client_socket.sendall(raw_request_frame)

        # Read incoming response frames
        print("\n[LISTENING FOR INCOMING RESPONSE FRAMES...]")
        response_frame = client_socket.recv(1024)

        if response_frame:
            print(f"\n[INCOMING RESPONSE FRAME] ({len(response_frame)} bytes):")
            print(f"HEX: {hex_format(response_frame)}")
        else:
            print("[-] Connection closed by device without returning data.")

        client_socket.close()

    except socket.timeout:
        print(f"[-] Connection or Read Timed Out after {TIMEOUT} seconds.")
    except Exception as e:
        print(f"[!] Socket Error: {e}")

if __name__ == "__main__":
    read_device_frames_as_client(LOGGER_IP, LOGGER_PORT)