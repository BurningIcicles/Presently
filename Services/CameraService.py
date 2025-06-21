# CameraService is used to return output from a given source, by default laptop screen
import cv2
import numpy as np
from typing import Optional, Tuple, Generator
import threading
import time

class CameraService:
    """
    Service for accessing and managing device camera functionality.
    Supports both webcam and screen capture capabilities.
    """

    def __init__(self, camera_index: int = 0, resolution: Tuple[int, int] = (640, 480)):
        """
        Initialize the camera service.

        Args:
            camera_index (int): Index of the camera device (0 for default webcam)
            resolution (tuple): Camera resolution (width, height)
        """
        self.camera_index = camera_index
        self.resolution = resolution
        self.camera = None
        self.is_capturing = False
        self._capture_thread = None

    def initialize_camera(self) -> bool:
        """
        Initialize and open the camera device.

        Returns:
            bool: True if camera opened successfully, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            if not self.camera.isOpened():
                print(f"Error: Could not open camera at index {self.camera_index}")
                return False

            print(f"Camera initialized successfully at index {self.camera_index}")
            return True

        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False

    def get_available_cameras(self) -> list:
        """
        Get list of available camera devices.

        Returns:
            list: List of available camera indices
        """
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
        if self.camera is None or not self.camera.isOpened():
            if not self.initialize_camera():
                return None

        ret, frame = self.camera.read()
        if ret:
            return frame
        else:
            print("Error: Could not capture frame")
            return None

    def start_capture(self) -> bool:
        """
        Start continuous camera capture in a separate thread.

        Returns:
            bool: True if capture started successfully
        """
        if self.is_capturing:
            print("Camera is already capturing")
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
        self.is_capturing = False
        if self._capture_thread:
            self._capture_thread.join(timeout=1.0)

    def _capture_loop(self):
        """Internal method for continuous capture loop."""
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
        try:
            cv2.imwrite(filename, frame)
            return True
        except Exception as e:
            print(f"Error saving frame: {e}")
            return False

    def record_video(self, output_filename: str, duration: int = 10) -> bool:
        """
        Record video for a specified duration.

        Args:
            output_filename (str): Output video filename
            duration (int): Recording duration in seconds

        Returns:
            bool: True if recording completed successfully
        """
        if not self.initialize_camera():
            return False

        # Get camera properties for video writer
        fps = int(self.camera.get(cv2.CAP_PROP_FPS))
        width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                frame = self.capture_frame()
                if frame is not None:
                    out.write(frame)
                else:
                    break

            out.release()
            print(f"Video saved to {output_filename}")
            return True

        except Exception as e:
            print(f"Error recording video: {e}")
            out.release()
            return False

    def release(self):
        """Release camera resources."""
        self.stop_capture()
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()

    def __enter__(self):
        """Context manager entry."""
        self.initialize_camera()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
