# CameraController is used to run the camera service functions
import sys
import os

# Add the parent directory to the path so we can import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Services.CameraService import CameraService
# Example usage and testing
if __name__ == "__main__":
    # Test camera access
    camera_service = CameraService()
    
    # Check available cameras
    available_cameras = camera_service.get_available_cameras()
    print(f"Available cameras: {available_cameras}")
    
    # Capture a single frame
    frame = camera_service.capture_frame()
    if frame is not None:
        print("Frame captured successfully!")
        # Save the frame
        camera_service.save_frame(frame, "test_frame.jpg")
    
    # Record a short video
    camera_service.record_video("test_video.mp4", duration=5)
    
    # Clean up
    camera_service.release()