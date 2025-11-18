import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import time
import os

# Try to import MediaPipe; if unavailable we'll fall back to OpenCV Haar cascade
try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
    mp_face_detection = mp.solutions.face_detection
except Exception:
    HAS_MEDIAPIPE = False

# Simple face-capture -> rage-comic stylizer
# Workflow:
# 1. Open webcam and detect faces using Haar cascade
# 2. When a face is found, wait 3 seconds
# 3. Capture the frame, crop to largest face, create circular face image
# 4. Apply a cartoon / "rage comic" style (edge exaggeration, posterize, bold eyes/mouth placeholders)
# 5. Save output to ./outputs with timestamp


CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'


def ensure_outputs_dir():
    out_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


# Mirror live preview (selfie view) when True
MIRROR_PREVIEW = True


def imshow_mirror(window_name, img, mirror=True, annotations=None):
    """Show image in a window, optionally mirrored horizontally for user preview.

    annotations: optional list of dicts with keys:
        text: str, pos: (x,y), font, scale, color, thickness
    Annotations are drawn AFTER flipping so they remain readable when image is mirrored.
    """
    try:
        do_mirror = MIRROR_PREVIEW and mirror
        # perform flip first if needed
        shown = cv2.flip(img, 1) if do_mirror else img.copy()

        # draw annotations after flipping so text stays readable
        if annotations:
            for ann in annotations:
                text = ann.get('text')
                pos = ann.get('pos', (10, 30))
                font = ann.get('font', cv2.FONT_HERSHEY_SIMPLEX)
                scale = ann.get('scale', 0.9)
                color = ann.get('color', (255, 255, 255))
                thickness = ann.get('thickness', 2)
                outline = ann.get('outline', True)

                # if mirrored, adjust x coordinate so annotation stays in same visual place
                x, y = pos
                if do_mirror:
                    # compute text pixel width to place same anchored position after flip
                    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness if not outline else max(1, thickness))
                    # anchor from left: convert to position from right
                    x = shown.shape[1] - x - tw

                if outline:
                    # draw thicker dark outline then main text
                    cv2.putText(shown, text, (x, y), font, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
                cv2.putText(shown, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)

        cv2.imshow(window_name, shown)
    except Exception:
        try:
            cv2.imshow(window_name, img)
        except Exception:
            pass


def capture_face_image(wait_seconds=3, label=None):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError('Could not open camera')
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

    if HAS_MEDIAPIPE:
        mp_detector = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
    else:
        mp_detector = None
    print('Looking for faces. Press Ctrl+C to quit.')

    captured = None
    try:
        # stability tracking: keep recent centers
        recent_centers = []
        stable_required = 10  # number of frames with low movement
        movement_threshold = 6  # pixels

        # smoothing / hold parameters to avoid flicker when detection is intermittent
        last_box = None  # (x, y, w, h) last drawn box
        last_seen = 0
        hold_frames = 6  # number of frames to keep showing last_box when detection is lost
        smooth_alpha = 0.45  # smoothing factor (0=no smoothing, 1=jump to new box)

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            if HAS_MEDIAPIPE and mp_detector is not None:
                # MediaPipe expects RGB
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = mp_detector.process(rgb)
                faces = []
                if results.detections:
                    for det in results.detections:
                        bbox = det.location_data.relative_bounding_box
                        x = int(bbox.xmin * frame.shape[1])
                        y = int(bbox.ymin * frame.shape[0])
                        w = int(bbox.width * frame.shape[1])
                        h = int(bbox.height * frame.shape[0])
                        faces.append((x, y, w, h))
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

            display = frame.copy()

            if len(faces) > 0:
                # pick largest face
                faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
                x, y, w, h = faces[0]

                # compute center and track stability
                cx = x + w // 2
                cy = y + h // 2
                recent_centers.append((cx, cy))
                if len(recent_centers) > stable_required:
                    recent_centers.pop(0)

                # smooth box coordinates with previous one to reduce jitter
                if last_box is None:
                    smooth_box = (x, y, w, h)
                else:
                    lx, ly, lw, lh = last_box
                    sx = int(lx * (1 - smooth_alpha) + x * smooth_alpha)
                    sy = int(ly * (1 - smooth_alpha) + y * smooth_alpha)
                    sw = int(lw * (1 - smooth_alpha) + w * smooth_alpha)
                    sh = int(lh * (1 - smooth_alpha) + h * smooth_alpha)
                    smooth_box = (sx, sy, sw, sh)

                last_box = smooth_box
                last_seen = 0

                # draw smoothed rectangle
                bx, by, bw, bh = smooth_box
                cv2.rectangle(display, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)

                # check movement over recent centers
                stable = False
                if len(recent_centers) >= stable_required:
                    dx = max(c[0] for c in recent_centers) - min(c[0] for c in recent_centers)
                    dy = max(c[1] for c in recent_centers) - min(c[1] for c in recent_centers)
                    if dx <= movement_threshold and dy <= movement_threshold:
                        stable = True

                # draw stability hint
                status_text = 'Stable' if stable else 'Hold still...'
                color = (0, 255, 0) if stable else (0, 165, 255)
                # use smoothed box coords for label placement when available
                label_x, label_y = (bx, by) if last_box is not None else (x, y)
                cv2.putText(display, status_text, (label_x, label_y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                # show a small circular preview of the face on the top-left
                face_crop = crop_to_face(frame, (x, y, w, h), pad=0.2)
                try:
                    pil_crop = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
                    circ = circular_mask_image(pil_crop)
                    circ = circ.resize((120, 120))
                    circ_np = cv2.cvtColor(np.array(circ), cv2.COLOR_RGBA2BGRA)
                    # paste preview into display (top-left corner)
                    h0, w0 = circ_np.shape[:2]
                    overlay = display.copy()
                    # create an alpha blend
                    if overlay.shape[2] == 3:
                        overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2BGRA)
                    overlay[10:10+h0, 10:10+w0] = circ_np
                    display = cv2.cvtColor(overlay, cv2.COLOR_BGRA2BGR)
                    # draw a label next to the preview (e.g. "Player 1 face")
                    lab = (label + ' face') if label else 'Face'
                    try:
                        tx = 10 + w0 + 12
                        ty = 30
                        cv2.putText(display, lab, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 4, cv2.LINE_AA)
                        cv2.putText(display, lab, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2, cv2.LINE_AA)
                    except Exception:
                        pass
                except Exception:
                    # fallback: just draw the rectangle if preview fails
                    # still draw a simple label in top-left
                    lab = (label + ' face') if label else 'Face'
                    try:
                        cv2.putText(display, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 4, cv2.LINE_AA)
                        cv2.putText(display, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2, cv2.LINE_AA)
                    except Exception:
                        pass

                # ensure the whole face bbox is fully inside the frame (not clipped)
                margin = 5
                fully_in_frame = (x > margin and y > margin and x + w < frame.shape[1] - margin and y + h < frame.shape[0] - margin)

                # only start countdown when stable and fully inside the camera frame
                if stable and fully_in_frame:
                    # build a ready display without player labels (start from raw frame)
                    try:
                        disp_ready = frame.copy()
                        cv2.rectangle(disp_ready, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        # paste circular preview if available
                        try:
                            overlay = disp_ready.copy()
                            if overlay.shape[2] == 3:
                                overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2BGRA)
                            overlay[10:10+h0, 10:10+w0] = circ_np
                            disp_ready = cv2.cvtColor(overlay, cv2.COLOR_BGRA2BGR)
                        except Exception:
                            pass
                        cx = frame.shape[1] // 2
                        cy = frame.shape[0] // 2
                        # don't draw the ready text onto the image itself — we'll draw it after
                        # mirroring via imshow_mirror so the text stays readable (not mirrored)
                    except Exception:
                        disp_ready = display.copy()

                    # show the ready display in a separate unmirrored window so the main preview
                    # isn't overwritten by other updates
                    ready_win = 'Face Capture - Ready'
                    # show mirrored image but draw the ready text after flip (so text is not mirrored)
                    annotations = [
                        {
                            'text': 'ready to take picture',
                            'pos': (cx - 200, cy - 20),
                            'font': cv2.FONT_HERSHEY_SIMPLEX,
                            'scale': 1.0,
                            'color': (255, 255, 255),
                            'thickness': 2,
                            'outline': True,
                        }
                    ]
                    imshow_mirror(ready_win, disp_ready, mirror=True, annotations=annotations)
                    if cv2.waitKey(1000) & 0xFF == 27:
                        try:
                            cv2.destroyWindow(ready_win)
                        except Exception:
                            pass
                        break

                    # then perform a numeric countdown (wait_seconds seconds) showing large centered numbers
                    for s in range(wait_seconds, 0, -1):
                        try:
                            disp2 = disp_ready.copy()
                            cx = frame.shape[1] // 2
                            cy = frame.shape[0] // 2
                            # draw the large countdown number as an annotation so it is drawn after flip
                            ann = {
                                'text': str(s),
                                'pos': (cx - 30, cy + 40),
                                'font': cv2.FONT_HERSHEY_SIMPLEX,
                                'scale': 3.0,
                                'color': (0, 255, 0),
                                'thickness': 4,
                                'outline': True,
                            }
                        except Exception:
                            disp2 = display.copy()
                            ann = {
                                'text': f'Capturing in {s}s',
                                'pos': (x, y - 10),
                                'font': cv2.FONT_HERSHEY_SIMPLEX,
                                'scale': 0.9,
                                'color': (0, 255, 0),
                                'thickness': 2,
                                'outline': True,
                            }
                        # countdown frames shown in the separate mirrored window with annotation
                        imshow_mirror(ready_win, disp2, mirror=True, annotations=[ann])
                        if cv2.waitKey(1000) & 0xFF == 27:
                            try:
                                cv2.destroyWindow(ready_win)
                            except Exception:
                                pass
                            break

                    # take one more frame as capture
                    ret2, frame2 = cap.read()
                    if ret2:
                        captured = frame2
                    break

                else:
                    # show the non-capturing display to user (single window)
                    # draw a simple label even when preview not present
                    lab = (label + ' face') if label else 'Face'
                    try:
                        cv2.putText(display, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 4, cv2.LINE_AA)
                        cv2.putText(display, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2, cv2.LINE_AA)
                    except Exception:
                        pass
                    imshow_mirror('Face Capture', display)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break

            # show the general live camera frame in the same single window (with label)
            try:
                lab = (label + ' face') if label else 'Face'
                cv2.putText(frame, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 4, cv2.LINE_AA)
                cv2.putText(frame, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2, cv2.LINE_AA)
            except Exception:
                pass
            # if detection disappeared this frame, optionally show the last_box for a few frames
            if last_box is not None and len(faces) == 0:
                # hold last box for a few frames to avoid flicker
                if last_seen < hold_frames:
                    bx, by, bw, bh = last_box
                    fb = frame.copy()
                    cv2.rectangle(fb, (bx, by), (bx + bw, by + bh), (0, 200, 0), 2)
                    try:
                        cv2.putText(fb, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 4, cv2.LINE_AA)
                        cv2.putText(fb, lab, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2, cv2.LINE_AA)
                    except Exception:
                        pass
                    imshow_mirror('Face Capture', fb)
                    last_seen += 1
                else:
                    # give up holding after hold_frames
                    last_box = None
                    imshow_mirror('Face Capture', frame)
            else:
                imshow_mirror('Face Capture', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if captured is None:
        raise RuntimeError('No frame captured')

    return captured, faces[0] if len(faces) > 0 else None


def capture_two_faces(wait_seconds=3, label1=None, label2=None):
    """Wait until two faces are detected, both stable and fully inside the frame,
    then perform a countdown and capture a single frame. Returns (frame, [face1, face2]).
    face entries are (x, y, w, h) for the two largest faces found.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError('Could not open camera')
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

    if HAS_MEDIAPIPE:
        mp_detector = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
    else:
        mp_detector = None
    print('Looking for two faces. Press Ctrl+C to quit.')

    captured = None
    try:
        recent_centers = []
        stable_required = 10
        movement_threshold = 6

        # smoothing/hold for two-face mode
        last_boxes = None  # [(x1,y1,w1,h1),(x2,y2,w2,h2)]
        last_seen = 0
        hold_frames = 6
        smooth_alpha = 0.45

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            if HAS_MEDIAPIPE and mp_detector is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = mp_detector.process(rgb)
                faces = []
                if results.detections:
                    for det in results.detections:
                        bbox = det.location_data.relative_bounding_box
                        x = int(bbox.xmin * frame.shape[1])
                        y = int(bbox.ymin * frame.shape[0])
                        w = int(bbox.width * frame.shape[1])
                        h = int(bbox.height * frame.shape[0])
                        faces.append((x, y, w, h))
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = list(face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)))


            if len(faces) >= 2:
                # choose two largest faces
                faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)[:2]
                (x1, y1, w1, h1), (x2, y2, w2, h2) = faces

                # smooth boxes if we have previous ones
                if last_boxes is None:
                    sb1 = (x1, y1, w1, h1)
                    sb2 = (x2, y2, w2, h2)
                else:
                    lx1, ly1, lw1, lh1 = last_boxes[0]
                    lx2, ly2, lw2, lh2 = last_boxes[1]
                    sb1 = (int(lx1 * (1 - smooth_alpha) + x1 * smooth_alpha),
                           int(ly1 * (1 - smooth_alpha) + y1 * smooth_alpha),
                           int(lw1 * (1 - smooth_alpha) + w1 * smooth_alpha),
                           int(lh1 * (1 - smooth_alpha) + h1 * smooth_alpha))
                    sb2 = (int(lx2 * (1 - smooth_alpha) + x2 * smooth_alpha),
                           int(ly2 * (1 - smooth_alpha) + y2 * smooth_alpha),
                           int(lw2 * (1 - smooth_alpha) + w2 * smooth_alpha),
                           int(lh2 * (1 - smooth_alpha) + h2 * smooth_alpha))
                last_boxes = (sb1, sb2)
                last_seen = 0

                display = frame.copy()
                x1, y1, w1, h1 = sb1
                x2, y2, w2, h2 = sb2
                cv2.rectangle(display, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                cv2.rectangle(display, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)
                
                cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
                cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
                recent_centers.append(((cx1, cy1), (cx2, cy2)))
                if len(recent_centers) > stable_required:
                    recent_centers.pop(0)

                display = frame.copy()
                cv2.rectangle(display, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                cv2.rectangle(display, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)

                stable1 = stable2 = False
                if len(recent_centers) >= stable_required:
                    xs1 = [c[0][0] for c in recent_centers]
                    ys1 = [c[0][1] for c in recent_centers]
                    xs2 = [c[1][0] for c in recent_centers]
                    ys2 = [c[1][1] for c in recent_centers]
                    dx1 = max(xs1) - min(xs1)
                    dy1 = max(ys1) - min(ys1)
                    dx2 = max(xs2) - min(xs2)
                    dy2 = max(ys2) - min(ys2)
                    if dx1 <= movement_threshold and dy1 <= movement_threshold:
                        stable1 = True
                    if dx2 <= movement_threshold and dy2 <= movement_threshold:
                        stable2 = True

                status_text = f"{'Stable' if (stable1 and stable2) else 'Hold still...'}"
                color = (0, 255, 0) if (stable1 and stable2) else (0, 165, 255)
                cv2.putText(display, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                # show small previews and labels
                try:
                    crop1 = crop_to_face(frame, (x1, y1, w1, h1), pad=0.2)
                    crop2 = crop_to_face(frame, (x2, y2, w2, h2), pad=0.2)
                    p1 = Image.fromarray(cv2.cvtColor(crop1, cv2.COLOR_BGR2RGB))
                    p2 = Image.fromarray(cv2.cvtColor(crop2, cv2.COLOR_BGR2RGB))
                    c1 = circular_mask_image(p1).resize((100, 100))
                    c2 = circular_mask_image(p2).resize((100, 100))
                    c1_np = cv2.cvtColor(np.array(c1), cv2.COLOR_RGBA2BGRA)
                    c2_np = cv2.cvtColor(np.array(c2), cv2.COLOR_RGBA2BGRA)
                    # place them top-left and top-right
                    if display.shape[2] == 3:
                        display = cv2.cvtColor(display, cv2.COLOR_BGR2BGRA)
                    h0, w0 = c1_np.shape[:2]
                    display[10:10+h0, 10:10+w0] = c1_np
                    display[10:10+h0, -10-w0:-10] = c2_np
                    # labels
                    lab1 = (label1 + ' face') if label1 else 'Player 1 face'
                    lab2 = (label2 + ' face') if label2 else 'Player 2 face'
                    cv2.putText(display, lab1, (10 + w0 + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3, cv2.LINE_AA)
                    cv2.putText(display, lab1, (10 + w0 + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 1, cv2.LINE_AA)
                    cv2.putText(display, lab2, (-10-w0-140, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3, cv2.LINE_AA)
                    cv2.putText(display, lab2, (-10-w0-140, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 1, cv2.LINE_AA)
                    display = cv2.cvtColor(display, cv2.COLOR_BGRA2BGR)
                except Exception:
                    pass

                # ensure both faces fully in frame
                margin = 5
                fully1 = (x1 > margin and y1 > margin and x1 + w1 < frame.shape[1] - margin and y1 + h1 < frame.shape[0] - margin)
                fully2 = (x2 > margin and y2 > margin and x2 + w2 < frame.shape[1] - margin and y2 + h2 < frame.shape[0] - margin)

                if stable1 and stable2 and fully1 and fully2:
                    # build a ready display from raw frame without player labels
                    try:
                        disp_ready = frame.copy()
                        cv2.rectangle(disp_ready, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                        cv2.rectangle(disp_ready, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)
                        try:
                            if disp_ready.shape[2] == 3:
                                overlay = cv2.cvtColor(disp_ready.copy(), cv2.COLOR_BGR2BGRA)
                            else:
                                overlay = disp_ready.copy()
                            overlay[10:10+h0, 10:10+w0] = c1_np
                            overlay[10:10+h0, -10-w0:-10] = c2_np
                            disp_ready = cv2.cvtColor(overlay, cv2.COLOR_BGRA2BGR)
                        except Exception:
                            pass
                        cx = frame.shape[1] // 2
                        cy = frame.shape[0] // 2
                        # don't paint the ready text onto the image; use annotation so text
                        # is drawn after mirroring and remains readable
                    except Exception:
                        disp_ready = display.copy()

                    # two-face ready display: show unmirrored in separate window so main preview
                    # remains active and doesn't overwrite the countdown
                    ready_win = 'Face Capture - Ready'
                    annotations = [
                        {
                            'text': 'ready to take picture',
                            'pos': (cx - 200, cy - 20),
                            'font': cv2.FONT_HERSHEY_SIMPLEX,
                            'scale': 1.0,
                            'color': (255, 255, 255),
                            'thickness': 2,
                            'outline': True,
                        }
                    ]
                    imshow_mirror(ready_win, disp_ready, mirror=True, annotations=annotations)
                    if cv2.waitKey(1000) & 0xFF == 27:
                        try:
                            cv2.destroyWindow(ready_win)
                        except Exception:
                            pass
                        break

                    for s in range(wait_seconds, 0, -1):
                        try:
                            disp2 = disp_ready.copy()
                            cx = frame.shape[1] // 2
                            cy = frame.shape[0] // 2
                            ann = {
                                'text': str(s),
                                'pos': (cx - 30, cy + 40),
                                'font': cv2.FONT_HERSHEY_SIMPLEX,
                                'scale': 3.0,
                                'color': (0, 255, 0),
                                'thickness': 4,
                                'outline': True,
                            }
                        except Exception:
                            disp2 = display.copy()
                            ann = {
                                'text': f'Capturing in {s}s',
                                'pos': (10, frame.shape[0] - 30),
                                'font': cv2.FONT_HERSHEY_SIMPLEX,
                                'scale': 0.9,
                                'color': (0, 255, 0),
                                'thickness': 2,
                                'outline': True,
                            }
                        imshow_mirror(ready_win, disp2, mirror=True, annotations=[ann])
                        if cv2.waitKey(1000) & 0xFF == 27:
                            try:
                                cv2.destroyWindow(ready_win)
                            except Exception:
                                pass
                            break

                    ret2, frame2 = cap.read()
                    if ret2:
                        captured = frame2
                    break

                else:
                    imshow_mirror('Face Capture', display)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break

            # show live frame while waiting for two faces
            try:
                cv2.putText(frame, 'Waiting for 2 faces...', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200,200,200), 2)
            except Exception:
                pass
            # if faces dropped, show last_boxes for a short hold to avoid flicker
            if last_boxes is not None and len(faces) < 2:
                if last_seen < hold_frames:
                    fb = frame.copy()
                    (bx1, by1, bw1, bh1), (bx2, by2, bw2, bh2) = last_boxes
                    cv2.rectangle(fb, (bx1, by1), (bx1 + bw1, by1 + bh1), (0, 200, 0), 2)
                    cv2.rectangle(fb, (bx2, by2), (bx2 + bw2, by2 + bh2), (0, 200, 0), 2)
                    imshow_mirror('Face Capture', fb)
                    last_seen += 1
                else:
                    last_boxes = None
                    imshow_mirror('Face Capture', frame)
            else:
                imshow_mirror('Face Capture', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if captured is None:
        raise RuntimeError('No frame captured')

    # recompute faces on the captured frame to return accurate boxes
    gray = cv2.cvtColor(captured, cv2.COLOR_BGR2GRAY)
    faces = list(face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)))
    if len(faces) < 2:
        # fallback: return the two previously found areas (best-effort)
        return captured, []
    faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)[:2]
    return captured, faces


def crop_to_face(frame, face_rect, pad=0.4):
    x, y, w, h = face_rect
    cx = x + w // 2
    cy = y + h // 2
    size = int(max(w, h) * (1.0 + pad))
    x0 = max(0, cx - size // 2)
    y0 = max(0, cy - size // 2)
    x1 = min(frame.shape[1], x0 + size)
    y1 = min(frame.shape[0], y0 + size)
    crop = frame[y0:y1, x0:x1]
    return crop


def circular_mask_image(pil_img):
    w, h = pil_img.size
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, w, h), fill=255)
    result = Image.new('RGBA', (w, h))
    result.paste(pil_img.convert('RGBA'), (0, 0), mask=mask)
    return result


def stylize_rage_comic(pil_img):
    # Produce a bold, high-contrast rage-comic style (black ink on white)
    base = pil_img.convert('RGB')
    base = ImageOps.fit(base, (512, 512))

    # Use OpenCV bilateral filter to smooth colors while preserving edges
    bgr = cv2.cvtColor(np.array(base), cv2.COLOR_RGB2BGR)
    smooth = cv2.bilateralFilter(bgr, d=9, sigmaColor=75, sigmaSpace=75)

    # Convert to grayscale and detect strong edges
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1=50, threshold2=150)
    # Thicken edges for bold comic ink
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)

    # Create white canvas and draw black edges
    canvas = np.ones((512, 512, 3), dtype=np.uint8) * 255
    canvas[edges != 0] = (0, 0, 0)

    # Convert canvas to PIL and draw exaggerated comedic features
    pil_canvas = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)).convert('RGBA')
    draw = ImageDraw.Draw(pil_canvas)
    w, h = pil_canvas.size

    # Exaggerated eyes with thick borders
    eye_w = w // 6
    eye_h = h // 6
    lx = w // 3 - eye_w // 2
    ly = h // 3 - eye_h // 2
    rx = 2 * w // 3 - eye_w // 2
    ry = ly
    # thick black border then white fill
    draw.ellipse((lx - 8, ly - 8, lx + eye_w + 8, ly + eye_h + 8), fill='black')
    draw.ellipse((lx, ly, lx + eye_w, ly + eye_h), fill='white')
    draw.ellipse((rx - 8, ry - 8, rx + eye_w + 8, ry + eye_h + 8), fill='black')
    draw.ellipse((rx, ry, rx + eye_w, ry + eye_h), fill='white')
    # pupils
    pup_w = eye_w // 3
    pup_h = eye_h // 3
    draw.ellipse((lx + eye_w // 2 - pup_w // 2, ly + eye_h // 2 - pup_h // 2, lx + eye_w // 2 + pup_w // 2, ly + eye_h // 2 + pup_h // 2), fill='black')
    draw.ellipse((rx + eye_w // 2 - pup_w // 2, ry + eye_h // 2 - pup_h // 2, rx + eye_w // 2 + pup_w // 2, ry + eye_h // 2 + pup_h // 2), fill='black')

    # Angry eyebrows
    draw.line((lx - 10, ly - 20, lx + eye_w + 10, ly - 5), fill='black', width=10)
    draw.line((rx - 10, ry - 20, rx + eye_w + 10, ry - 5), fill='black', width=10)

    # Big open mouth (black border with white inner and tooth lines)
    mouth_w = w // 2
    mouth_h = h // 5
    mx = w // 2 - mouth_w // 2
    my = 2 * h // 3 - mouth_h // 2
    draw.ellipse((mx - 12, my - 12, mx + mouth_w + 12, my + mouth_h + 12), fill='black')
    draw.ellipse((mx + 6, my + 6, mx + mouth_w - 6, my + mouth_h - 6), fill='white')
    # teeth lines
    teeth = 6
    for i in range(1, teeth):
        tx = mx + i * (mouth_w // teeth)
        draw.line((tx, my + 6, tx, my + mouth_h - 6), fill='black', width=4)

    return pil_canvas


def stylize_cute(pil_img):
    """Produce a cute, soft stylized avatar: smooth colors, big eyes, blush and a small smile."""
    base = pil_img.convert('RGBA')
    base = ImageOps.fit(base, (512, 512))

    # smooth colors with bilateral filter
    bgr = cv2.cvtColor(np.array(base.convert('RGB')), cv2.COLOR_RGB2BGR)
    smooth = cv2.bilateralFilter(bgr, d=9, sigmaColor=100, sigmaSpace=75)
    img = Image.fromarray(cv2.cvtColor(smooth, cv2.COLOR_BGR2RGB)).convert('RGBA')
    draw = ImageDraw.Draw(img, 'RGBA')
    w, h = img.size

    # big white eyes
    eye_r = w // 12
    lx = w // 3
    rx = 2 * w // 3
    eye_y = h // 3
    draw.ellipse((lx - eye_r, eye_y - eye_r, lx + eye_r, eye_y + eye_r), fill=(255, 255, 255, 255))
    draw.ellipse((rx - eye_r, eye_y - eye_r, rx + eye_r, eye_y + eye_r), fill=(255, 255, 255, 255))

    # pupils (slightly low for cute look)
    pup_r = max(3, eye_r // 3)
    draw.ellipse((lx - pup_r, eye_y, lx + pup_r, eye_y + pup_r * 2), fill=(40, 40, 40, 255))
    draw.ellipse((rx - pup_r, eye_y, rx + pup_r, eye_y + pup_r * 2), fill=(40, 40, 40, 255))

    # sparkles
    draw.ellipse((lx + eye_r - 6, eye_y - eye_r + 6, lx + eye_r - 2, eye_y - eye_r + 10), fill=(255, 255, 255, 255))
    draw.ellipse((rx - eye_r + 2, eye_y - eye_r + 6, rx - eye_r + 6, eye_y - eye_r + 10), fill=(255, 255, 255, 255))

    # small smiling mouth (soft arc)
    mx = w // 2
    my = 2 * h // 3
    mouth_box = (mx - 28, my - 8, mx + 28, my + 18)
    draw.arc(mouth_box, start=0, end=180, fill=(150, 40, 80, 255), width=6)

    # blush cheeks
    blush_r = w // 18
    draw.ellipse((lx - blush_r - 6, my - 4, lx - 6, my + blush_r), fill=(255, 140, 170, 120))
    draw.ellipse((rx + 6, my - 4, rx + blush_r + 6, my + blush_r), fill=(255, 140, 170, 120))

    # gentle warm overlay for pastel toning
    overlay = Image.new('RGBA', img.size, (255, 240, 240, 30))
    img = Image.alpha_composite(img, overlay)

    return img


# Pixel-art stylizer function (map to small grid + palette)
def stylize_sprite(pil_img, sprite_size=32, scale=12, palette_mode='default'):
    """Convert the circular face image into a pixel-sprite using a small palette.
    sprite_size: the small pixel grid size (e.g., 24)
    scale: upscale factor for final PNG (sprite_size * scale)
    """
    small = pil_img.convert('RGBA').resize((sprite_size, sprite_size), resample=Image.NEAREST)

    # palette choices: default (reference) or 'cute' (pastel)
    if palette_mode == 'cute':
        palette = [
            (70, 50, 30, 255),    # outline
            (255, 220, 140, 255),  # soft yellow / skin
            (220, 180, 90, 255),   # soft shadow
            (255, 245, 200, 255),  # highlight
            (255, 120, 170, 255),  # mouth pink
            (255, 190, 210, 255),  # light pink
            (120, 200, 140, 255),  # soft green eye
            (180, 140, 110, 255),  # mid brown
        ]
    else:
        # palette sampled/tuned to match the provided reference sprite
        palette = [
            (60, 48, 18, 255),     # dark outline / border
            (245, 213, 40, 255),   # main yellow
            (190, 144, 22, 255),   # darker side shade
            (255, 245, 120, 255),  # highlight (bright yellow)
            (206, 30, 130, 255),   # mouth magenta / dark pink
            (255, 150, 200, 255),  # mouth light pink
            (45, 95, 30, 255),     # green eye
            (120, 110, 90, 255),   # mid brown / metal accent
        ]

    pal = np.array(palette, dtype=np.int32)
    arr = np.array(small)
    h, w = arr.shape[:2]
    out = np.zeros((h, w, 4), dtype=np.uint8)
    # Heuristics to force yellow style:
    # - If pixel is bluish, map it toward yellow palette
    # - Preserve pink/magenta for mouth if strongly pink
    # - Preserve green for eyes if strongly green
    for y in range(h):
        for x in range(w):
            px = arr[y, x]
            # preserve transparency outside circular mask
            if px[3] < 30:
                out[y, x] = (0, 0, 0, 0)
                continue
            r, g, b, a = px

            # detect mouth-like magenta/pink
            if r > 180 and g < 120 and b > 130:
                # map to mouth pinks in palette (index 4 or 5)
                out[y, x] = palette[4] if r < 230 else palette[5]
                continue

            # detect green eyes
            if g > 90 and r < 120 and b < 100:
                out[y, x] = palette[6]
                continue

            # detect bluish pixels and remap toward yellow / pastel depending on mode
            if b > r and b > g and b > 100:
                out[y, x] = palette[3] if x > w * 0.6 else palette[1]
                continue

            # otherwise choose nearest yellow/brown in palette by color distance
            d = np.sum((pal[:, :3] - px[:3]) ** 2, axis=1)
            best = int(np.argmin(d))
            out[y, x] = tuple(pal[best])

    # Upscale using nearest neighbor to keep pixelated look
    final = Image.fromarray(out, mode='RGBA').resize((sprite_size * scale, sprite_size * scale), resample=Image.NEAREST)

    # Add a 1-pixel outline by detecting transparent->opaque edges
    final_np = np.array(final)
    alpha = final_np[:, :, 3]
    edges = cv2.Canny(alpha, 1, 255)
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
    # paint edges dark
    final_np[edges != 0] = (24, 24, 24, 255)
    return Image.fromarray(final_np, mode='RGBA')


def make_rage_face():
    out_dir = ensure_outputs_dir()
    frame, face = capture_face_image(wait_seconds=3)
    if face is None:
        raise RuntimeError('No face detected')

    crop = crop_to_face(frame, face, pad=0.5)
    pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    circ = circular_mask_image(pil)
    # Create a hand-drawn line-art sketch for preview
    def line_art(pil_img):
        gray = pil_img.convert('L')
        arr = np.array(gray)
        gx = cv2.Sobel(arr, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(arr, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.hypot(gx, gy)
        edges = (edges / edges.max() * 255).astype(np.uint8)
        sketch = Image.fromarray(edges).convert('L').point(lambda p: 255 if p > 50 else 0)
        sketch = ImageOps.invert(sketch).convert('RGBA')
        return sketch

    # generate cute styled and sprite previews
    styled = stylize_cute(circ)
    sprite = stylize_sprite(circ, palette_mode='cute')

    # show side-by-side preview: original cropped circular image, cute styled, and pixel sprite
    orig_np = cv2.cvtColor(np.array(circ.resize((512, 512))), cv2.COLOR_RGBA2BGRA)
    styl_np = cv2.cvtColor(np.array(styled.resize((512, 512))), cv2.COLOR_RGBA2BGRA)
    sprite_np = cv2.cvtColor(np.array(sprite.resize((512, 512))), cv2.COLOR_RGBA2BGRA)

    # compose a display image: left original, middle styled, right sprite
    display_h = 512
    display_w = 512 * 3
    display_img = np.zeros((display_h, display_w, 4), dtype=np.uint8)
    display_img[:, 0:512] = orig_np
    display_img[:, 512:1024] = styl_np
    display_img[:, 1024:1536] = sprite_np

    # convert to BGR for OpenCV display
    display_bgr = cv2.cvtColor(display_img, cv2.COLOR_RGBA2BGR)
    window_title = 'Capture Preview (original | stylized | sketch) - s=save, q=quit'
    imshow_mirror(window_title, display_bgr)


    # interactive save/quit loop (no auto-save) - require explicit 's' to save or 'q' to quit
    saved = False
    print("Preview shown. Press 's' to save, 'q' to quit without saving.")
    while True:
        key = cv2.waitKey(0) & 0xFF
        # s -> save
        if key == ord('s'):
            saved = True
            break
        # q or ESC -> quit without saving
        if key in (ord('q'), 27):
            saved = False
            break

    cv2.destroyAllWindows()

    if saved:
        # save stylized and pixel art versions
        ts = int(time.time())
        # save sprite as primary output and also save styled version
        filename_sprite = os.path.join(out_dir, f'rage_face_sprite_{ts}.png')
        filename_styled = os.path.join(out_dir, f'rage_face_{ts}.png')
        sprite.save(filename_sprite)
        styled.save(filename_styled)
        print('Saved:', filename_sprite, filename_styled)
        return filename_sprite
    else:
        print('Preview closed without saving')
        return None


if __name__ == '__main__':
    make_rage_face()
