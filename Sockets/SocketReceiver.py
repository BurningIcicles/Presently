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
        s.bind((host, port))
        s.listen()
        print('📡 Listening for commands...')
        conn, addr = s.accept()
        with conn:
            print(f'🔗 Connected by {addr}')
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(f"📨 Received: {data}")
                lcd.display(data)

start_server()

