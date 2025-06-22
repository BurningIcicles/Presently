from RPLCD.i2c import CharLCD
from time import sleep

class LCDService:
    def display(self, message="Hello World", delay=0.3):
        """Display message on LCD with proper scrolling."""
        self.lcd = CharLCD('PCF8574', 0x27)
        self.lcd.clear()
        self.lcd.write_string(message)
        self.width = 16