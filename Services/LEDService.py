import RPi.GPIO as GPIO
import time

def LEDService():
    def __init__(self):
        self.pin = 17 #GPIO17 = Pin 11

    def light(self, blink_count):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)  # GPIO17 = Pin 11
        for i in range(blink_count):
            GPIO.output(17, GPIO.HIGH)  # LED ON
            time.sleep(0.5)
            GPIO.output(17, GPIO.LOW)   # LED OFF
            time.sleep(0.5)
        GPIO.cleanup()
