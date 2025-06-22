from RPLCD.i2c import CharLCD
from time import sleep

class LCDService:
    def __init__(self):
        self.lcd = CharLCD('PCF8574', 0x27)
        self.lcd.clear()
        self.width = 16

    def display(self, message = "Hello World", delay = 0.3, loop = True):
        while True:
            for i in range(len(message) - self.width + 1):
                self.lcd.clear()
                self.lcd.write_string(message[i:i + self.width])
                sleep(delay)
            
            if not loop:
                break
