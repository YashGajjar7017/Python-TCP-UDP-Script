import socket
import threading
from datetime import datetime

# Server Configuration
HOST = '192.168.4.1'
PORT = 80          # Change to your ESP32's target port (e.g., 80, 8080, 8888)
BUFFER_SIZE = 4096

def handle_client(client_socket, client_address):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟢 Connection from {client_address[0]}:{client_address[1]}")
    
    try:
        # Receive incoming data from the Android app
        data = client_socket.recv(BUFFER_SIZE)
        
        if data:
            print("=" * 60)
            print("RECEIVED DATA (RAW):")
            print(data)
            print("-" * 60)
            print("RECEIVED DATA (DECODED STRING):")
            try:
                print(data.decode('utf-8'))
            except UnicodeDecodeError:
                # If non-UTF8/binary protocol, print hex representation
                print(f"[Binary Data Hex]: {data.hex()}")
            print("=" * 60)

            # Send a mock response back to the app (Standard HTTP 200 OK)
            # If your ESP32 uses a custom TCP binary response, replace this string
            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n"
                "\r\n"
                "OK"
            )
            client_socket.sendall(http_response.encode('utf-8'))
            print("✅ Sent mock '200 OK' response to app.")
            
    except Exception as e:
        print(f"❌ Error handling client: {e}")
    finally:
        client_socket.close()
        print(f"🔴 Connection with {client_address[0]} closed.\n")

def start_server():
    # Create TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow immediate reuse of the port to avoid "Address already in use" errors
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print("*" * 60)
        print(f"🚀 Server running!")
        print(f"📡 Listening on IP: {HOST} | Port: {PORT}")
        print("Waiting for incoming app requests... (Press Ctrl+C to stop)")
        print("*" * 60)

        while True:
            client_socket, client_address = server_socket.accept()
            # Handle each connection in a new thread so the server doesn't block
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, client_address)
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()