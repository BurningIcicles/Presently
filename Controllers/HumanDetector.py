# HumanDetector.py
import cv2
import numpy as np
import mediapipe as mp
import sys
import os
from collections import deque
from time import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Sockets.SocketSender import SocketSender


# MediaPipe
mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()
face = mp_face.FaceMesh(refine_landmarks=True)

# Movement tracking
hand_q = deque(maxlen=10)
hip_q = deque(maxlen=10)
head_q = deque(maxlen=10)
leg_q = deque(maxlen=10)
last_alert = ""
last_time = 0
still_start_time = None

def send_alert(msg):
    global last_alert, last_time
    now = time()
    if msg != last_alert and now - last_time > 5:
        print(f"[ALERT] {msg}")
        last_alert = msg
        last_time = now

# Replace this with your actual camera or use OpenCV VideoCapture for quick test
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    pose_result = pose.process(rgb)
    face_result = face.process(rgb)

    alert = None

    if pose_result.pose_landmarks:
        lms = pose_result.pose_landmarks.landmark

        # Draw green bounding box around person
        xs = [lm.x for lm in lms]
        ys = [lm.y for lm in lms]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        start_point = (int(min_x * w), int(min_y * h))
        end_point = (int(max_x * w), int(max_y * h))
        cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)


        # Hand fidgeting (right wrist)
        rw = lms[mp_pose.PoseLandmark.RIGHT_WRIST]
        hand_q.append((rw.x, rw.y))
        if len(hand_q) > 5:
            deltas = [np.linalg.norm(np.subtract(hand_q[i], hand_q[i-1])) for i in range(1, len(hand_q))]
            if np.mean(deltas) > 0.01:
                sender = SocketSender()
                sender.send_command("FIDGETING_HANDS")
                alert = "Stop fidgeting hands"

        # Hip swaying
        lhip = lms[mp_pose.PoseLandmark.LEFT_HIP]
        rhip = lms[mp_pose.PoseLandmark.RIGHT_HIP]
        hips = ((lhip.x + rhip.x)/2, (lhip.y + rhip.y)/2)
        hip_q.append(hips)
        if len(hip_q) > 5:
            deltas = [np.linalg.norm(np.subtract(hip_q[i], hip_q[i-1])) for i in range(1, len(hip_q))]
            if np.mean(deltas) > 0.005:
                sender = SocketSender()
                sender.send_command("STOP_SWAYING")
                alert = "Stop swaying"

        lankle = lms[mp_pose.PoseLandmark.LEFT_ANKLE]
        rankle = lms[mp_pose.PoseLandmark.RIGHT_ANKLE]

        # Only check movement if both ankles are visible with high confidence
        if lankle.visibility > 0.6 and rankle.visibility > 0.6:
            legs = ((lankle.x + rankle.x)/2, (lankle.y + rankle.y)/2)
            leg_q.append(legs)
            if len(leg_q) > 5:
                deltas = [np.linalg.norm(np.subtract(leg_q[i], leg_q[i-1])) for i in range(1, len(leg_q))]
                if np.mean(deltas) > 0.005:
                    sender = SocketSender()
                    sender.send_command("SWINGING_LEGS")
                    alert = "Stop swinging legs"
        else:
            leg_q.clear()  # reset queue if legs go invisible


        if face_result.multi_face_landmarks:
            nose = face_result.multi_face_landmarks[0].landmark[1]
            head_q.append((nose.x, nose.y))

            if len(head_q) > 5:
                deltas = [np.linalg.norm(np.subtract(head_q[i], head_q[i - 1])) for i in range(1, len(head_q))]
                movement = np.mean(deltas)

                if movement < 0.003:
                    if still_start_time is None:
                        still_start_time = time()
                    elif time() - still_start_time > 5:
                        sender = SocketSender()
                        sender.send_command("MOVE_HEAD")
                        alert = "Move your head"
                else:
                    still_start_time = None


    if alert:
        send_alert(alert)

    cv2.imshow("Pose Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
