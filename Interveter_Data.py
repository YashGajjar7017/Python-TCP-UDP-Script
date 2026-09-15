import serial
import time
import struct

# CONFIGURATION
COM_PORT = "COM3"  # Update this to your active COM port (e.g., COM4)
BAUD_RATES = [9600, 115200, 19200, 4800]  # Standard inverter baud rates
SLAVE_IDS = [1, 2, 3, 247]  # Most common inverter slave IDs

def calculate_crc16(data: bytes) -> bytes:
    """Calculate Modbus RTU 16-bit CRC checksum."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def build_read_holding_request(slave_id, start_addr=0, count=2):
    """Build raw Modbus RTU frame (Function Code 03)."""
    payload = struct.pack('>BBHH', slave_id, 3, start_addr, count)
    crc = calculate_crc16(payload)
    return payload + crc

def test_rs485_connection():
    print(f"Scanning RS485 direct connection on {COM_PORT}...\n" + "=" * 50)
    
    for baud in BAUD_RATES:
        print(f"\n[+] Testing Baud Rate: {baud}")
        try:
            ser = serial.Serial(
                port=COM_PORT,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5
            )
            
            for slave_id in SLAVE_IDS:
                request = build_read_holding_request(slave_id, start_addr=0, count=2)
                ser.reset_input_buffer()
                ser.write(request)
                time.sleep(0.1)
                
                response = ser.read(100)
                if len(response) >= 5:
                    print(f"  ---> SUCCESS! Response on Baud {baud} | Slave ID {slave_id}")
                    print(f"       Raw Hex Output: {response.hex().upper()}")
                    ser.close()
                    return
            ser.close()
        except Exception as e:
            print(f"  [-] Serial Error on {COM_PORT}: {e}")
            break

    print("\n[-] No valid Modbus RTU response detected. Swap A+ and B- wires if needed.")

if __name__ == "__main__":
    test_rs485_connection()