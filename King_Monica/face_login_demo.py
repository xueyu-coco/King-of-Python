"""Simple face capture helper used by the demo.

Function provided:
 - capture_and_make_sprite(label) -> path to saved image or None

This is a minimal helper that opens the default webcam using OpenCV,
lets the user press 'c' or SPACE to capture a frame, saves a resized
PNG under King_Monica/captures/, and returns the saved path.

Requirements: pip install opencv-python
"""
from __future__ import annotations

import os
import time
from typing import Optional


def capture_and_make_sprite(label: str) -> Optional[str]:
    """Open the default camera, capture a frame on key press and save it.

    Controls:
      - Press 'c' or SPACE to capture and save
      - Press 'q' or ESC to cancel and return None

    Returns the absolute path to the saved PNG on success, or None on cancel/error.
    """
    try:
        import cv2
    except Exception as e:
        print("OpenCV is required for face capture (pip install opencv-python).", e)
        return None

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return None

    captures_dir = os.path.join(os.path.dirname(__file__), "captures")
    os.makedirs(captures_dir, exist_ok=True)

    window_name = f"Capture - {label} (press C or SPACE to capture, Q to cancel)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    saved_path = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera.")
                break

            # show a flipped preview (like a mirror) to help framing
            preview = cv2.flip(frame, 1)
            cv2.imshow(window_name, preview)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') or key == 32:  # 'c' or SPACE
                # Save a resized square PNG
                h, w = frame.shape[:2]
                side = min(w, h)
                # center crop
                cx, cy = w // 2, h // 2
                x0 = max(0, cx - side // 2)
                y0 = max(0, cy - side // 2)
                crop = frame[y0:y0 + side, x0:x0 + side]
                sprite = cv2.resize(crop, (80, 80), interpolation=cv2.INTER_AREA)

                timestamp = int(time.time())
                fname = f"{label}_{timestamp}.png"
                path = os.path.join(captures_dir, fname)
                cv2.imwrite(path, sprite)
                saved_path = os.path.abspath(path)
                print(f"Captured and saved: {saved_path}")
                break
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("Capture cancelled by user")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return saved_path
