import RPi.GPIO as GPIO
import time

class LEDService:
    def light(self, blink_count):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)  # GPIO17 = Pin 7
        for i in range(blink_count):
            GPIO.output(17, GPIO.HIGH)  # LED ON
            time.sleep(0.5)
            GPIO.output(17, GPIO.LOW)   # LED OFF
            time.sleep(0.5)
        GPIO.cleanup()
