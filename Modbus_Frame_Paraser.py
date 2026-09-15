import socket
import time

TARGET_IP = "192.168.88.88"
PORT = 8899  # Typical pass-through port

# Standard Modbus RTU Read Request: Slave ID 01, Func 03, Addr 0000, Length 0002, CRC C40B
RAW_MODBUS_RTU_REQ = bytes.fromhex("01 03 00 00 00 02 C4 0B")

def test_serial_passthrough():
    print(f"Sending raw Modbus RTU frame over TCP to {TARGET_IP}:{PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((TARGET_IP, PORT))
        
        sock.send(RAW_MODBUS_RTU_REQ)
        time.sleep(0.2)
        
        response = sock.recv(1024)
        sock.close()
        
        if response:
            print(f"[+] Received Response ({len(response)} bytes): {response.hex().upper()}")
            print("The device is using Serial-over-TCP transparent bridge mode!")
        else:
            print("[-] Connected, but no response received from inverter CPU.")
    except Exception as e:
        print(f"[-] Connection Error: {e}")

if __name__ == "__main__":
    test_serial_passthrough()