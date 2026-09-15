from pymodbus.client import ModbusSerialClient

# Initialize Modbus RTU Client
client = ModbusSerialClient(
    port="/dev/ttyUSB0",  # Update to match your USB adapter port
    baudrate=9600,
    parity="N",
    stopbits=1,
    bytesize=8,
    timeout=1,
)

if client.connect():
    # Read PV1 Voltage & Current (Registers 31001 - 31002)
    response = client.read_holding_registers(address=31001, count=2, slave=1)

    if not response.isError():
        pv1_voltage = response.registers[0] / 10.0  # 0.1V scale
        pv1_current = response.registers[1] / 10.0  # 0.1A scale

        print(f"PV1 Voltage: {pv1_voltage} V")
        print(f"PV1 Current: {pv1_current} A")
    else:
        print("Failed to read registers from inverter.")

    client.close()