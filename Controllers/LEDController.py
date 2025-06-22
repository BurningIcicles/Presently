import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Services.LEDService import LEDService

if __name__ == "__main__":
    led_service = LEDService()
    led_service.light(5)