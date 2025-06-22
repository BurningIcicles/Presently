import cv2
import numpy as np
import time
import sys
import os

# Add parent path to import CameraService
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Services.CameraService import CameraService

# Path to model and label file
model_path = os.path.join(os.path.dirname(__file__), "..", "Model", "detect.tflite")
labelmap_path = os.path.join(os.path.dirname(__file__), "..", "Model", "labelmap.txt")

# Try loading labels from labelmap.txt, fallback to ["person"] if not found
try:
    with open(labelmap_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    PERSON_CLASS_ID = labels.index("person") if "person" in labels else 0
    print(f"Loaded labelmap.txt with {len(labels)} labels.")
except Exception as e:
    print(f"⚠️ Could not load labelmap.txt: {e}")
    labels = ["person"]
    PERSON_CLASS_ID = 0  # Assume "person" is class 0

# Load TFLite model
from tflite_runtime.interpreter import Interpreter
# Or use this if you use full TensorFlow:
# from tensorflow.lite.python.interpreter import Interpreter

interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]['shape']
input_height = input_shape[1]
input_width = input_shape[2]

# Initialize camera
camera = CameraService()
camera.initialize_camera()

print("🟢 Human detection started. Press 'q' to quit.")

while True:
    frame = camera.capture_frame()
    if frame is None:
        continue

    # Resize to model input size
    input_frame = cv2.resize(frame, (input_width, input_height))
    input_data = np.expand_dims(input_frame, axis=0).astype(np.uint8)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    classes = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]

    height, width, _ = frame.shape

    PERSON_CLASS_ID = 0

    for i in range(len(scores)):
        class_id = int(classes[i])
        score = scores[i]

        print(f"[DEBUG] class={class_id}, score={score:.2f}")

        if score > 0.5 and class_id == PERSON_CLASS_ID:
            # Bounding box coordinates are normalized (0.0 to 1.0)
            ymin, xmin, ymax, xmax = boxes[i]
            (left, top, right, bottom) = (int(xmin * width), int(ymin * height),
                                          int(xmax * width), int(ymax * height))

            # Draw the bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Optional: Draw label
            label = f"Person: {int(score * 100)}%"
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    cv2.imshow("Human Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
