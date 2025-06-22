# SocketReceiver.py (inside Presently/Sockets)

import os
import sys
import socket

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Services.LEDService import LEDService

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
                            lcd_service = LCDService()
                            led_service = LEDService()
                            led_service.light(7)
                            if data == "STOP_SWAYING":
                                # run code when they need to stop swaying
                                lcd_service.display("Stop fidgeting hands")
                            elif data == "SWINGING_LEGS":
                                # run code when they need to swinging legs
                                lcd_service.display("Stop swinging legs")
                            elif data == "MOVE_HEAD":
                                # run code when they need to move their head
                                lcd_service.display("Move your head")
                            elif data == "FIDGETING_HANDS":
                                # run code when they need to stop fidgeting with their hands
                                lcd_service.display("Stop fidgeting hands")

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
