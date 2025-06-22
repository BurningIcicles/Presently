# socket_server.py
import socket

def start_server():
    host = '0.0.0.0'
    port = 5001

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print('Listening for commands...')
        conn, addr = s.accept()
        with conn:
            print(f'Connected by {addr}')
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(f"Received: {data}")
                if data == "SHOW_TEXT":
                    # Display to LCD here
                    print("Triggering LCD!")

start_server()
