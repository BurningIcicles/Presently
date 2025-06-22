import cv2
import numpy as np
import time
import sys
import os
import mediapipe as mp

# Add parent path to import CameraService
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Services.CameraService import CameraService

# Path to model and label file
model_path = os.path.join(os.path.dirname(__file__), "..", "Model", "detect.tflite")
labelmap_path = os.path.join(os.path.dirname(__file__), "..", "Model", "labelmap.txt")

# Load labels
try:
    with open(labelmap_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    PERSON_CLASS_ID = labels.index("person") if "person" in labels else 0
    print(f"Loaded labelmap.txt with {len(labels)} labels.")
except Exception as e:
    print(f"⚠️ Could not load labelmap.txt: {e}")
    labels = ["person"]
    PERSON_CLASS_ID = 0

# Load TFLite SSD model
from tflite_runtime.interpreter import Interpreter
interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']
input_height = input_shape[1]
input_width = input_shape[2]

# Initialize MediaPipe components
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh

pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False)
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize camera
camera = CameraService()
camera.initialize_camera()

print("🟢 Person detection + full skeleton + face mesh started. Press 'q' to quit.")

while True:
    frame = camera.capture_frame()
    if frame is None:
        continue

    height, width, _ = frame.shape

    # Resize to SSD input
    input_frame = cv2.resize(frame, (input_width, input_height))
    input_data = np.expand_dims(input_frame, axis=0).astype(np.uint8)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    classes = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]

    PERSON_CLASS_ID = 0

    for i in range(len(scores)):
        class_id = int(classes[i])
        score = scores[i]

        if score > 0.5 and class_id == PERSON_CLASS_ID:
            ymin, xmin, ymax, xmax = boxes[i]
            box_margin = 20  # pixels to expand in all directions

            left = max(0, int(xmin * width) - box_margin)
            top = max(0, int(ymin * height) - box_margin)
            right = min(width, int(xmax * width) + box_margin)
            bottom = min(height, int(ymax * height) + box_margin)
            # Draw bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            label = f"Person: {int(score * 100)}%"
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Crop to person area
            person_crop = frame[top:bottom, left:right]
            if person_crop.size == 0:
                continue

            crop_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)

            # Process pose (skeleton)
            pose_results = pose.process(crop_rgb)
            if pose_results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image=person_crop,
                    landmark_list=pose_results.pose_landmarks,
                    connections=mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
                )

            # Process face mesh (head)
            face_results = face_mesh.process(crop_rgb)
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=person_crop,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing.DrawingSpec(
                            color=(80, 110, 10), thickness=1, circle_radius=1
                        )
                    )

            # Paste back annotated crop
            frame[top:bottom, left:right] = person_crop

    cv2.imshow("Full Body + FaceMesh", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

