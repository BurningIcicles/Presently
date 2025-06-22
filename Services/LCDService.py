from RPLCD.i2c import CharLCD
from time import sleep

class LCDService:
    def display(self, message="Hello World", delay=0.3):
        """Display message on LCD with proper scrolling."""
        self.lcd = CharLCD('PCF8574', 0x27)
        self.lcd.clear()
        self.lcd.write_string(message)
        self.width = 16

        sleep(delay * 3)
        # Always run through the message once (do-while behavior)
        while True:
            # Scroll from left to right (beginning to end)
            for i in range(len(message) - self.width + 1):
                self.lcd.clear()
                self.lcd.write_string(message[i:i + self.width])
                if (i == len(message) - self.width + 1):
                    sleep(delay * 3)
                else:
                    sleep(delay)
