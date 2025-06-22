# SocketReceiver.py (inside Presently/Sockets)

import os
import sys
import socket

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Step 2: Now you can import LCDService
from Services.LCDService import LCDService

def start_server():
    lcd = LCDService()
    host = '0.0.0.0'
    port = 5001

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
        s.bind((host, port))
        s.listen()
        print('Listening for commands...')

        while True:  # Keep server running
            try:
                conn, addr = s.accept()
                print(f'Connected by {addr}')

                with conn:
                    while True:
                        try:
                            data = conn.recv(1024).decode()
                            if not data:
                                print(f'Client {addr} disconnected')
                                break
                            print(f"Received: {data}")
                            if data == "SHOW_TEXT":
                                # Display to LCD here
                                print("Triggering LCD!")
                                # Add your LCD code here
                                lcd.display(data)

                            # Send acknowledgment back to client
                            conn.send(b"OK")

                        except ConnectionResetError:
                            print(f'Client {addr} connection reset')
                            break
                        except Exception as e:
                            print(f"Error receiving data: {e}")
                            break

            except KeyboardInterrupt:
                print("Server stopped by user")
                break
            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue

if __name__ == "__main__":
    start_server()
