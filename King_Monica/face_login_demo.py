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

    captures_dir = os.path.join(os.path.dirname(__file__), "captures")
    os.makedirs(captures_dir, exist_ok=True)

    # If a recent capture for this label already exists (from a previous quick capture), return it
    try:
        recent = sorted([os.path.join(captures_dir, f) for f in os.listdir(captures_dir) if f.startswith(label + "_")], key=os.path.getmtime, reverse=True)
        if recent:
            # if the most recent file is newer than 10 seconds, return it to support sequential calls
            if time.time() - os.path.getmtime(recent[0]) < 10:
                return os.path.abspath(recent[0])
    except Exception:
        pass

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return None

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

            # draw a dashed circular guide in the preview to help users center their face
            try:
                ph, pw = preview.shape[:2]
                # inner padding should match compose_head inner padding approx
                inner_padding = 24
                diameter = max(8, min(pw, ph) - inner_padding * 2)
                radius = int(diameter // 2)
                center = (pw // 2, ph // 2)

                # dashed circle parameters
                dash_deg = 12
                gap_deg = 8
                thickness = 2
                color = (0, 255, 0)  # green guide

                for start in range(0, 360, dash_deg + gap_deg):
                    end = start + dash_deg
                    cv2.ellipse(preview, center, (radius, radius), 0, start, end, color, thickness)
            except Exception:
                # if anything fails drawing the guide, ignore and continue
                pass

            cv2.imshow(window_name, preview)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') or key == 32:  # 'c' or SPACE
                # Detect faces and save one or two sprites depending on detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                try:
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                except Exception:
                    faces = ()

                h, w = frame.shape[:2]
                timestamp = int(time.time())

                if len(faces) >= 2:
                    # sort faces by x (left to right)
                    faces = sorted(faces, key=lambda r: r[0])
                    saved_paths = []
                    for i, (x, y, fw, fh) in enumerate(faces[:2]):
                        crop = frame[y:y+fh, x:x+fw]
                        sprite = cv2.resize(crop, (80, 80), interpolation=cv2.INTER_AREA)
                        # create circular alpha mask and save as PNG with transparency
                        try:
                            import numpy as np
                            h, w = sprite.shape[:2]
                            mask = np.zeros((h, w), dtype=np.uint8)
                            radius = min(w, h) // 2
                            center = (w // 2, h // 2)
                            cv2.circle(mask, center, radius, 255, -1)
                            b, g, r = cv2.split(sprite)
                            bgra = cv2.merge([b, g, r, mask])
                            fname = f"Face{i+1}_{timestamp}.png"
                            path = os.path.join(captures_dir, fname)
                            cv2.imwrite(path, bgra)
                            saved_paths.append(os.path.abspath(path))
                            print(f"Captured face {i+1}: {path}")
                        except Exception:
                            # fallback to saving without alpha
                            fname = f"Face{i+1}_{timestamp}.png"
                            path = os.path.join(captures_dir, fname)
                            cv2.imwrite(path, sprite)
                            saved_paths.append(os.path.abspath(path))
                            print(f"Captured face {i+1} (no alpha): {path}")
                    # return appropriate face based on label if possible
                    if 'Face1' in label:
                        saved_path = saved_paths[0]
                    elif 'Face2' in label:
                        saved_path = saved_paths[1]
                    else:
                        saved_path = saved_paths[0]
                    break

                # If only one face or none detected, fallback to center crop
                side = min(w, h)
                cx, cy = w // 2, h // 2
                x0 = max(0, cx - side // 2)
                y0 = max(0, cy - side // 2)
                crop = frame[y0:y0 + side, x0:x0 + side]
                sprite = cv2.resize(crop, (80, 80), interpolation=cv2.INTER_AREA)

                # save with circular alpha mask so the PNG is circular
                try:
                    import numpy as np
                    h2, w2 = sprite.shape[:2]
                    mask = np.zeros((h2, w2), dtype=np.uint8)
                    radius = min(w2, h2) // 2
                    center = (w2 // 2, h2 // 2)
                    cv2.circle(mask, center, radius, 255, -1)
                    b, g, r = cv2.split(sprite)
                    bgra = cv2.merge([b, g, r, mask])
                    fname = f"{label}_{timestamp}.png"
                    path = os.path.join(captures_dir, fname)
                    cv2.imwrite(path, bgra)
                    saved_path = os.path.abspath(path)
                    print(f"Captured and saved: {saved_path}")
                except Exception:
                    # fallback to saving without alpha
                    fname = f"{label}_{timestamp}.png"
                    path = os.path.join(captures_dir, fname)
                    cv2.imwrite(path, sprite)
                    saved_path = os.path.abspath(path)
                    print(f"Captured and saved (no alpha): {saved_path}")
                break
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("Capture cancelled by user")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return saved_path
