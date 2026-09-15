import socket
import struct
import time

# Target gateway IP address
TARGET_IP = "192.168.88.88"  # Replace with your gateway IP address
TARGET_PORTS = [502, 8899, 8889, 4897, 8080]  # Common Modbus TCP ports

def build_modbus_tcp_request(unit_id, start_addr, count):
    """Constructs a raw Modbus TCP Read Holding Registers (0x03) frame."""
    transaction_id = 0x0001
    protocol_id = 0x0000  # Modbus protocol
    length = 6            # Remaining bytes in request
    function_code = 0x03  # Read Holding Registers
    
    # Pack into binary format
    return struct.pack('>HHHBBHH', transaction_id, protocol_id, length, unit_id, function_code, start_addr, count)

def test_modbus_communication():
    print(f"Testing Unbranded Inverter Modbus TCP on {TARGET_IP}...\n" + "=" * 50)
    
    for port in TARGET_PORTS:
        print(f"\n[+] Testing TCP Port: {port}")
        for unit_id in range(1, 11):  # Test Modbus Slave IDs 1 through 10
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.5)
                sock.connect((TARGET_IP, port))
                
                # Request 2 registers starting at address 0
                request = build_modbus_tcp_request(unit_id=unit_id, start_addr=0, count=2)
                sock.send(request)
                
                response = sock.recv(1024)
                sock.close()
                
                if len(response) >= 9:
                    print(f"  ---> SUCCESS! Valid Modbus response from Port: {port} | Slave ID: {unit_id}")
                    # Unpack response payload
                    raw_data = struct.unpack(f'>{len(response)}B', response)
                    print(f"       Raw Hex Response: {[hex(x) for x in raw_data]}")
                    return True
            except Exception:
                pass
            time.sleep(0.05)
            
    print("\n[-] No Modbus TCP response received on tested ports/IDs.")
    return False

if __name__ == "__main__":
    test_modbus_communication()