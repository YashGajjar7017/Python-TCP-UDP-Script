import logging
import socket
from pysolarmanv5 import PySolarmanV5

# Enable debug logging to automatically intercept internal frame generation
logging.basicConfig(level=logging.DEBUG)

LOGGER_IP = "192.168.88.88"
LOGGER_SN = 1234567890  # Replace with your Wi-Fi Dongle S/N
LOGGER_PORT = 8899

# Initialize Solarman Client
modbus = PySolarmanV5(
    LOGGER_IP, LOGGER_SN, port=LOGGER_PORT, mb_slave_id=1, verbose=True
)

# 1. Manual Modbus RTU Frame: Read Holding Registers 31001 (0x7919), Count 2 (0x0002)
# Structure: [Slave ID, Function Code, Start Addr High, Start Addr Low, Quantity High, Quantity Low]
raw_modbus_req = bytearray([0x01, 0x03, 0x79, 0x19, 0x00, 0x02])

# Calculate Modbus RTU CRC16 and append
crc = modbus._calc_crc(raw_modbus_req)
raw_modbus_req.extend(crc.to_bytes(2, byteorder="little"))

print(f"\n[+] Raw Modbus Request Frame: {raw_modbus_req.hex(' ')}")

# 2. Encapsulate into Solarman V5 Frame & Send
v5_request_frame = modbus._v5_frame_encoder(raw_modbus_req)
print(f"[+] Complete Solarman V5 Outer Frame Sent: {v5_request_frame.hex(' ')}")

# 3. Receive Response Frame
v5_response_frame = modbus._send_receive(v5_request_frame)
print(
    f"[+] Complete Solarman V5 Outer Frame Received: {v5_response_frame.hex(' ')}"
)

# 4. Extract Modbus Payload from V5 Response Frame
modbus_reply = modbus._v5_frame_decoder(v5_response_frame)
print(f"[+] Extracted Modbus Response Payload: {modbus_reply.hex(' ')}")