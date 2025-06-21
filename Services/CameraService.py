# CameraService is used to return output from a given source, by default laptop screen
import cv2
import numpy as np
from typing import Optional, Tuple, Generator
import threading
import time
import platform
import subprocess

class CameraService:
    """
    Service for accessing and managing device camera functionality.
    Optimized for Raspberry Pi and other platforms.
    """

    def __init__(self, camera_index: int = 0, resolution: Tuple[int, int] = (640, 480)):
        """
        Initialize the camera service.

        Args:
            camera_index (int): Index of the camera device (0 for default webcam)
            resolution (tuple): Camera resolution (width, height)
        """
        print(f"Initializing CameraService with camera_index: {camera_index}, resolution: {resolution}")
        self.camera_index = camera_index
        self.resolution = resolution
        self.camera = None
        self.is_capturing = False
        self._capture_thread = None
        self.is_raspberry_pi = self._detect_raspberry_pi()
        print(f"Raspberry Pi detected: {self.is_raspberry_pi}")

    def _detect_raspberry_pi(self) -> bool:
        print("Detecting Raspberry Pi")
        """Detect if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False

    def initialize_camera(self) -> bool:
        """
        Initialize and open the camera device.
        Optimized for Raspberry Pi.

        Returns:
            bool: True if camera opened successfully, False otherwise
        """
        try:
            if self.is_raspberry_pi:
                return self._initialize_raspberry_pi_camera()
            else:
                return self._initialize_standard_camera()

        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False

    def _initialize_raspberry_pi_camera(self) -> bool:
        """Initialize camera specifically for Raspberry Pi."""
        print("Initializing Raspberry Pi camera...")
        
        # Try different approaches for Pi camera
        approaches = [
            self._try_pi_camera_v4l2,
            self._try_pi_camera_any,
            self._try_pi_camera_direct
        ]
        
        for approach in approaches:
            if approach():
                return True
        
        print("Failed to initialize Raspberry Pi camera with all approaches")
        return False

    def _try_pi_camera_v4l2(self) -> bool:
        """Try V4L2 backend for Pi camera."""
        try:
            self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
            
            if self.camera.isOpened():
                # Set properties for Pi
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                
                # Don't try to set FPS on Pi - let it use default
                print("Pi camera initialized with V4L2 backend")
                self._print_pi_camera_properties()
                return True
        except Exception as e:
            print(f"V4L2 approach failed: {e}")
        
        return False

    def _try_pi_camera_any(self) -> bool:
        """Try auto-detection backend for Pi camera."""
        try:
            self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_ANY)
            
            if self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                
                print("Pi camera initialized with auto-detection backend")
                self._print_pi_camera_properties()
                return True
        except Exception as e:
            print(f"Auto-detection approach failed: {e}")
        
        return False

    def _try_pi_camera_direct(self) -> bool:
        """Try direct camera access for Pi."""
        try:
            # Try without specifying backend
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                
                print("Pi camera initialized with direct access")
                self._print_pi_camera_properties()
                return True
        except Exception as e:
            print(f"Direct access approach failed: {e}")
        
        return False

    def _initialize_standard_camera(self) -> bool:
        """Initialize camera for non-Pi systems."""
        print("Initializing standard camera...")
        
        self.camera = cv2.VideoCapture(self.camera_index)
        
        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        # Try to set FPS (may not work on Pi)
        if not self.is_raspberry_pi:
            self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        if not self.camera.isOpened():
            print(f"Error: Could not open camera at index {self.camera_index}")
            return False
            
        print(f"Standard camera initialized successfully at index {self.camera_index}")
        return True

    def _print_pi_camera_properties(self):
        """Print camera properties for Raspberry Pi."""
        if self.camera is None or not self.camera.isOpened():
            return
        
        print("=== Raspberry Pi Camera Properties ===")
        properties = {
            'Width': cv2.CAP_PROP_FRAME_WIDTH,
            'Height': cv2.CAP_PROP_FRAME_HEIGHT,
            'FPS': cv2.CAP_PROP_FPS,
            'Brightness': cv2.CAP_PROP_BRIGHTNESS,
            'Contrast': cv2.CAP_PROP_CONTRAST,
            'Backend': cv2.CAP_PROP_BACKEND
        }
        
        for name, prop in properties.items():
            try:
                value = self.camera.get(prop)
                print(f"{name}: {value}")
            except Exception as e:
                print(f"{name}: Error - {e}")
        
        print("=====================================")

    def get_effective_fps(self) -> float:
        """
        Get the effective FPS that the camera is actually using.
        Optimized for Raspberry Pi.
        
        Returns:
            float: Effective FPS, or reasonable default for Pi
        """
        if self.camera is None or not self.camera.isOpened():
            return 15.0 if self.is_raspberry_pi else 30.0
        
        fps = self.camera.get(cv2.CAP_PROP_FPS)
        
        # If FPS is invalid, use Pi-appropriate default
        if fps <= 0:
            if self.is_raspberry_pi:
                print(f"Warning: Invalid FPS ({fps}), using Pi default 15 FPS")
                return 15.0
            else:
                print(f"Warning: Invalid FPS ({fps}), using default 30 FPS")
                return 30.0
        
        return fps

    def test_fps(self, duration: int = 5) -> float:
        """
        Test the actual FPS by capturing frames.
        Optimized for Raspberry Pi performance.
        
        Args:
            duration (int): Test duration in seconds
            
        Returns:
            float: Actual FPS achieved
        """
        if not self.initialize_camera():
            return 0.0
        
        start_time = time.time()
        frame_count = 0
        
        print(f"Testing FPS for {duration} seconds on {'Raspberry Pi' if self.is_raspberry_pi else 'standard system'}...")
        
        while time.time() - start_time < duration:
            frame = self.capture_frame()
            if frame is not None:
                frame_count += 1
            else:
                break
        
        actual_duration = time.time() - start_time
        actual_fps = frame_count / actual_duration if actual_duration > 0 else 0
        
        print(f"Captured {frame_count} frames in {actual_duration:.2f} seconds")
        print(f"Actual FPS: {actual_fps:.2f}")
        
        return actual_fps

    def record_video(self, output_filename: str, duration: int = 10) -> bool:
        """
        Record video for a specified duration.
        Optimized for Raspberry Pi.
        
        Args:
            output_filename (str): Output video filename
            duration (int): Recording duration in seconds
            
        Returns:
            bool: True if recording completed successfully
        """
        if not self.initialize_camera():
            return False
            
        # Get effective FPS (optimized for Pi)
        fps = self.get_effective_fps()
        width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Recording video with FPS: {fps}, Resolution: {width}x{height}")
        
        # Use Pi-optimized codec if available
        if self.is_raspberry_pi:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Better for Pi
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print("Error: Could not open video writer")
            return False
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < duration:
                frame = self.capture_frame()
                if frame is not None:
                    out.write(frame)
                    frame_count += 1
                else:
                    print("Failed to capture frame during recording")
                    break
                    
            out.release()
            actual_duration = time.time() - start_time
            actual_fps = frame_count / actual_duration if actual_duration > 0 else 0
            
            print(f"Video saved to {output_filename}")
            print(f"Recorded {frame_count} frames in {actual_duration:.2f} seconds")
            print(f"Actual FPS: {actual_fps:.2f}")
            return True

        except Exception as e:
            print(f"Error recording video: {e}")
            out.release()
            return False

    def get_available_cameras(self) -> list:
        """
        Get list of available camera devices to use in the camera_index parameter in the constructor

        Returns:
            list: List of available camera indices
        """
        print("Getting available cameras")
        available_cameras = []
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.

        Returns:
            np.ndarray: Captured frame as numpy array, or None if failed
        """
        print("Capturing frame")
        if self.camera is None or not self.camera.isOpened():
            if not self.initialize_camera():
                return None

        # self.camera.read() returns a boolean and the frame if it was captured
        frame_captured, frame = self.camera.read()
        print("frame_captured: ", frame_captured)
        if frame_captured:
            return frame

        print("Error: Could not capture frame")
        # Enhanced error logging
        self._log_camera_error()
        return None

    def _log_camera_error(self):
        """Log detailed camera error information."""
        print("=== Camera Error Details ===")
        
        # Check if camera object exists
        if self.camera is None:
            print("Error: Camera object is None")
            return
        
        # Check if camera is opened
        if not self.camera.isOpened():
            print("Error: Camera is not opened")
            return
        
        # Get camera properties for debugging
        try:
            width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            brightness = self.camera.get(cv2.CAP_PROP_BRIGHTNESS)
            
            print(f"Camera Properties:")
            print(f"  Width: {width}")
            print(f"  Height: {height}")
            print(f"  FPS: {fps}")
            print(f"  Brightness: {brightness}")
            
            # Check if properties are valid
            if width <= 0 or height <= 0:
                print("Error: Invalid camera resolution")
            if fps <= 0:
                print("Error: Invalid FPS setting")
                
        except Exception as e:
            print(f"Error getting camera properties: {e}")
        
        # Common troubleshooting steps
        print("\nTroubleshooting suggestions:")
        print("1. Check if camera is connected")
        print("2. Check if camera is being used by another application")
        print("3. Check camera permissions")
        print("4. Try a different camera index")
        print("5. Restart the camera service")
        
        # Try to get more specific error info
        try:
            # Try to read again to see if it's a temporary issue
            retry_captured, retry_frame = self.camera.read()
            print(f"Retry attempt - frame_captured: {retry_captured}")
            
            if not retry_captured:
                print("Error: Frame capture consistently failing")
                
        except Exception as e:
            print(f"Exception during retry: {e}")
        
        print("==========================")

    def start_capture(self) -> bool:
        """
        Start continuous camera capture in a separate thread.

        Returns:
            bool: True if capture started successfully
        """
        print("Starting capture")
        if self.is_capturing:
            print("Error: Camera is already capturing")
            return False

        if not self.initialize_camera():
            return False

        self.is_capturing = True
        self._capture_thread = threading.Thread(target=self._capture_loop)
        self._capture_thread.daemon = True
        self._capture_thread.start()
        return True

    def stop_capture(self):
        """Stop continuous camera capture."""
        print("Stopping capture")
        self.is_capturing = False
        if self._capture_thread:
            self._capture_thread.join(timeout=1.0)

    def _capture_loop(self):
        """Internal method for continuous capture loop."""
        print("Starting capture loop")
        while self.is_capturing:
            frame = self.capture_frame()
            if frame is not None:
                # Process frame here (e.g., send to AI analysis)
                self._process_frame(frame)
            time.sleep(0.033)  # ~30 FPS

    def _process_frame(self, frame: np.ndarray):
        """
        Process captured frame. Override this method for custom processing.

        Args:
            frame (np.ndarray): Captured frame to process
        """
        # Default implementation - can be overridden
        pass

    def get_frame_generator(self) -> Generator[np.ndarray, None, None]:
        """
        Get a generator that yields frames from the camera.

        Yields:
            np.ndarray: Captured frames
        """
        print("Getting frame generator")
        if not self.initialize_camera():
            return

        while True:
            frame = self.capture_frame()
            if frame is not None:
                yield frame
            else:
                break

    def save_frame(self, frame: np.ndarray, filename: str) -> bool:
        """
        Save a frame to a file.

        Args:
            frame (np.ndarray): Frame to save
            filename (str): Output filename

        Returns:
            bool: True if saved successfully
        """
        print("Saving frame")
        try:
            cv2.imwrite(filename, frame)
            return True
        except Exception as e:
            print(f"Error saving frame: {e}")
            return False

    def release(self):
        """Release camera resources."""
        print("Releasing camera")
        self.stop_capture()
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()

    def __enter__(self):
        """Context manager entry."""
        print("Entering context manager")
        self.initialize_camera()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        print("Exiting context manager")
        self.release()
