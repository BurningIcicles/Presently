# After detecting some CV event
import socket

def send_command():
    s = socket.socket()
    s.connect(("raspberrypi.local", 5001))  # or use Pi's IP
    s.send(b"SHOW_TEXT")
    s.close()