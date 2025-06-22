# After detecting some CV event
import socket

def send_command(data_message):
    s = socket.socket()
    pi_ip = "10.0.155.13"
    s.connect((pi_ip, 5001))  # or use Pi's IP
    s.send(data_message.encode())
    s.close()

if __name__ == "__main__":
    send_command()