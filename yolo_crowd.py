"""
yolo_crowd.py  —  Real-time crowd detection using YOLOv8
Places laptop webcam near ONE exit (Main_Entrance by default).
Detects people, maps count → crowd level, POSTs to Flask every 5s.

Run SEPARATELY from app.py:
    python yolo_crowd.py

Requirements:
    pip install ultralytics opencv-python requests
"""

import cv2
import time
import requests
import threading
from ultralytics import YOLO

# ──────────────────────────────────────────────────────────────
#  CONFIG  — change these if needed
# ──────────────────────────────────────────────────────────────
FLASK_URL      = "http://localhost:5000"   # your laptop's IP when sharing on LAN
CAMERA_EXIT    = "Main_Entrance"           # which exit this camera watches
UPDATE_INTERVAL= 5                         # seconds between Flask updates
WEBCAM_INDEX   = 0                         # 0 = built-in, 1 = external USB cam

# Crowd thresholds  (tune based on your demo space)
COUNT_LOW      = 3    # 0–2 people  → Low
COUNT_MED      = 7    # 3–6 people  → Medium
                      # 7+          → High

# ──────────────────────────────────────────────────────────────
#  GLOBALS
# ──────────────────────────────────────────────────────────────
model          = YOLO("yolov8n.pt")        # nano model — fast, downloads ~6 MB once
current_count  = 0
current_level  = "Low"
running        = True


def count_to_level(count: int) -> str:
    if count < COUNT_LOW:
        return "Low"
    elif count < COUNT_MED:
        return "Medium"
    return "High"


# ──────────────────────────────────────────────────────────────
#  BACKGROUND THREAD  — POST crowd to Flask
# ──────────────────────────────────────────────────────────────
def push_to_flask():
    global current_level
    while running:
        level = current_level
        try:
            resp = requests.post(
                f"{FLASK_URL}/api/crowd",
                json={CAMERA_EXIT: level},
                timeout=3
            )
            if resp.ok:
                print(f"[YOLO → Flask]  {CAMERA_EXIT}: {level}  ({current_count} people detected)")
            else:
                print(f"[YOLO] Flask error: {resp.status_code}")
        except Exception as e:
            print(f"[YOLO] Could not reach Flask: {e}")
        time.sleep(UPDATE_INTERVAL)


# ──────────────────────────────────────────────────────────────
#  MAIN LOOP  — webcam + YOLO inference
# ──────────────────────────────────────────────────────────────
def main():
    global current_count, current_level, running

    # start background push thread
    pusher = threading.Thread(target=push_to_flask, daemon=True)
    pusher.start()

    cap = cv2.VideoCapture(WEBCAM_INDEX)
    if not cap.isOpened():
        print("[YOLO] ERROR: Could not open webcam. Check WEBCAM_INDEX.")
        running = False
        return

    print(f"\n[YOLO] Camera started — watching exit: {CAMERA_EXIT}")
    print("[YOLO] Press Q in the preview window to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # run YOLOv8 detection (only class 0 = person)
        results = model(frame, classes=[0], verbose=False)[0]
        boxes   = results.boxes
        count   = len(boxes) if boxes is not None else 0

        current_count = count
        current_level = count_to_level(count)

        # ── draw overlay on preview window ──────────────
        level   = current_level
        color   = {"Low": (0, 200, 80), "Medium": (0, 165, 255), "High": (0, 0, 230)}[level]

        # bounding boxes
        for box in (boxes.xyxy.cpu().numpy() if boxes is not None else []):
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # status banner
        banner = f"  Exit: {CAMERA_EXIT}   |   People: {count}   |   Crowd: {level}  "
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 44), (20, 20, 30), -1)
        cv2.putText(frame, banner, (8, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2, cv2.LINE_AA)

        cv2.imshow("YOLO Crowd Detector — Emergency Exit System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    running = False
    cap.release()
    cv2.destroyAllWindows()
    print("[YOLO] Camera stopped.")


if __name__ == "__main__":
    main()
