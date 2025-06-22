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
        """Word wrapping - keeps words together."""
        words = message.split()
        
        if len(message) <= width:
            # Short message fits on first line
            return message, ""
        
        # Try to fit words on first line
        first_line = ""
        second_line = ""
        
        for word in words:
            # Check if word fits on first line
            if len(first_line + word) <= width:
                first_line += word + " "
            else:
                # Word goes to second line
                second_line += word + " "
        
        # Remove trailing spaces
        first_line = first_line.rstrip()
        second_line = second_line.rstrip()
        
        # If second line is too long, truncate it
        if len(second_line) > width:
            second_line = second_line[:width]
        
        return first_line, second_line