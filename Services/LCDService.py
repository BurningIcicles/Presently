from RPLCD.i2c import CharLCD
from time import sleep

class LCDService:
    def display(self, message="Hello World", delay=0.3):
        """Display message on LCD with proper scrolling."""

        self.width = 16
        first_line, second_line = self._wrap_text(message, self.width)

        self.lcd = CharLCD('PCF8574', 0x27)
        self.lcd.clear()
        self.lcd.write_string(first_line)
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(second_line)

    def _wrap_text(self, message, width=16):
        """Simple text wrapping - first 16 chars on line 1, rest on line 2."""
        if len(message) <= width:
            # Short message fits on first line
            return message, ""
        else:
            # Message wraps to second line
            first_line = message[:width]
            second_line = message[width:width * 2]  # Max 16 more chars
            return first_line, second_line