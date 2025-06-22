# CameraController is used to run the camera service functions
import sys
import os

# Add the parent directory to the path so we can import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Services.LCDService import LCDService

if __name__ == "__main__":
    LCDService = LCDService()
    LCDService.display("Stop swinging legs")