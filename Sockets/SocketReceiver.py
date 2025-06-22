# SocketReceiver.py (inside Presently/Sockets)

import os
import sys
import socket
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Services.LEDService import LEDService
from Services.LCDService import LCDService

def display_message(lcd_service, message):
    """Display message on LCD in a separate thread to avoid blocking."""
    try:
        lcd_service.display(message, loop=False)  # Don't loop, just display once
    except Exception as e:
        print(f"Error displaying message: {e}")

def blink_led(led_service, blink_count):
    """Blink LED in a separate thread to avoid blocking."""
    try:
        led_service.light(blink_count)
    except Exception as e:
        print(f"Error blinking LED: {e}")

def start_server():
    lcd_service = LCDService()
    led_service = LEDService()
    host = '0.0.0.0'
    port = 5001

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print('Listening for commands...')

        while True:
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
                            
                            # Handle commands with simple threading
                            if data == "STOP_SWAYING":
                                print("Displaying: Stop swaying")
                                # Run LCD display in separate thread
                                lcd_thread = threading.Thread(target=display_message, args=(lcd_service, "Stop swaying"))
                                lcd_thread.daemon = True
                                lcd_thread.start()
                                
                                # Run LED blink in separate thread
                                led_thread = threading.Thread(target=blink_led, args=(led_service, 3))
                                led_thread.daemon = True
                                led_thread.start()
                                
                            elif data == "SWINGING_LEGS":
                                print("Displaying: Stop swinging legs")
                                lcd_thread = threading.Thread(target=display_message, args=(lcd_service, "Stop swinging legs"))
                                lcd_thread.daemon = True
                                lcd_thread.start()
                                
                                led_thread = threading.Thread(target=blink_led, args=(led_service, 3))
                                led_thread.daemon = True
                                led_thread.start()
                                
                            elif data == "MOVE_HEAD":
                                print("Displaying: Move your head")
                                lcd_thread = threading.Thread(target=display_message, args=(lcd_service, "Move your head"))
                                lcd_thread.daemon = True
                                lcd_thread.start()
                                
                                led_thread = threading.Thread(target=blink_led, args=(led_service, 3))
                                led_thread.daemon = True
                                led_thread.start()
                                
                            elif data == "FIDGETING_HANDS":
                                print("Displaying: Stop fidgeting hands")
                                lcd_thread = threading.Thread(target=display_message, args=(lcd_service, "Stop fidgeting hands"))
                                lcd_thread.daemon = True
                                lcd_thread.start()
                                
                                led_thread = threading.Thread(target=blink_led, args=(led_service, 3))
                                led_thread.daemon = True
                                led_thread.start()

                            # Send acknowledgment back to client immediately
                            conn.send(b"OK")

                        except ConnectionResetError:
                            print(f'Client {addr} connection reset')
                            break
                        except ConnectionAbortedError:
                            print(f'Client {addr} connection aborted')
                            break
                        except Exception as e:
                            print(f"Error receiving data: {e}")
                            break
                
                print(f'Connection with {addr} closed, waiting for new connections...')
                            
            except KeyboardInterrupt:
                print("Server stopped by user")
                break
            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue

if __name__ == "__main__":
    start_server()
