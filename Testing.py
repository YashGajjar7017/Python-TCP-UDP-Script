import logging
from pysolarmanv5 import PySolarmanV5

# Enable debug logging to display the raw hex Request and Response frames
logging.basicConfig(level=logging.DEBUG)

# Config Details
LOGGER_IP = "192.168.88.88"
LOGGER_SN = 1234567890  # Replace with your logger's 10-digit serial number
LOGGER_PORT = 8899  # Standard Solarman V5 port (try 8899 or 4196)
SLAVE_ID = 1  # Modbus Slave ID

def main():
    try:
        print("Connecting to Wi-Fi Logger...")
        
        # Initialize the V5 connection (Handles framing & TCP socket)
        modbus = PySolarmanV5(
            LOGGER_IP, 
            LOGGER_SN, 
            port=LOGGER_PORT, 
            mb_slave_id=SLAVE_ID, 
            verbose=True
        )

        # Send Request & Get Response for PV1 Voltage & Current (Registers 31001-31002)
        # Function Code 0x03 (Read Holding Registers)
        start_register = 31001
        register_count = 2
        
        print(f"\nSending Modbus Read Request (Register: {start_register}, Count: {register_count})...")
        registers = modbus.read_holding_registers(register_addr=start_register, quantity=register_count)

        # Process and display values
        pv1_voltage = registers[0] / 10.0
        pv1_current = registers[1] / 10.0

        print("\n--- Parsed Response ---")
        print(f"PV1 Voltage : {pv1_voltage} V")
        print(f"PV1 Current : {pv1_current} A")

    except Exception as e:
        print(f"\nConnection Failed: {e}")

if __name__ == "__main__":
    main()