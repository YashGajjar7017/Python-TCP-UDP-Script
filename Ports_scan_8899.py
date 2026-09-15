import socket

# Bind to all local interfaces on your PC
HOST = '0.0.0.0'
PORT = 8899  # Change this to the destination port seen in Wireshark

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Server listening on port {PORT}... Waiting for Inverter connection...")

conn, addr = server.accept()
print(f"[+] Inverter Connected from: {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    print(f"Received Packet ({len(data)} bytes): {data.hex().upper()}")

conn.close()