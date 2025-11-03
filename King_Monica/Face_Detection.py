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


def capture_face_image(wait_seconds=3):
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

                display = frame.copy()
                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

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
                cv2.putText(display, status_text, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

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
                except Exception:
                    # fallback: just draw the rectangle if preview fails
                    pass

                # only start countdown when stable
                if stable:
                    for s in range(wait_seconds, 0, -1):
                        disp2 = display.copy()
                        cv2.putText(disp2, f'Capturing in {s}s', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        cv2.imshow('Face (will capture)', disp2)
                        if cv2.waitKey(1000) & 0xFF == 27:
                            break

                    # take one more frame as capture
                    ret2, frame2 = cap.read()
                    if ret2:
                        captured = frame2
                    break

                else:
                    # show the non-capturing display to user
                    cv2.imshow('Face (waiting)', display)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break

            cv2.imshow('Face (looking)', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if captured is None:
        raise RuntimeError('No frame captured')

    return captured, faces[0] if len(faces) > 0 else None


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

    styled = stylize_rage_comic(circ)
    sketch = line_art(pil)

    # show side-by-side preview: original cropped circular image and the hand-drawn line-art
    orig_np = cv2.cvtColor(np.array(circ.resize((512, 512))), cv2.COLOR_RGBA2BGRA)
    styl_np = cv2.cvtColor(np.array(styled.resize((512, 512))), cv2.COLOR_RGBA2BGRA)
    sketch_np = cv2.cvtColor(np.array(sketch.resize((512, 512))), cv2.COLOR_RGBA2BGRA)

    # compose a display image: left original, middle styled, right sketch
    display_h = 512
    display_w = 512 * 3
    display_img = np.zeros((display_h, display_w, 4), dtype=np.uint8)
    display_img[:, 0:512] = orig_np
    display_img[:, 512:1024] = styl_np
    display_img[:, 1024:1536] = sketch_np

    # convert to BGR for OpenCV display
    display_bgr = cv2.cvtColor(display_img, cv2.COLOR_RGBA2BGR)
    window_title = 'Capture Preview (original | stylized | sketch) - s=save, q=quit'
    cv2.imshow(window_title, display_bgr)

    # Pixel-art stylizer function (map to small grid + palette)
    def stylize_pixel_art(pil_img, out_size=48):
        # reduce to small size (pixelate)
        small = pil_img.convert('RGBA').resize((out_size, out_size), resample=Image.NEAREST)

        # palette tuned to the attached sprite (flattened)
        palette = [
            (24, 24, 24, 255),   # dark outline
            (221, 180, 27, 255),  # main yellow
            (170, 136, 22, 255),  # darker side
            (255, 233, 90, 255),  # highlight
            (230, 90, 170, 255),  # pink mouth
            (24, 120, 24, 255),   # green eye
            (0, 0, 0, 0),         # transparent
        ]

        arr = np.array(small)
        h, w = arr.shape[:2]
        out = np.zeros((h, w, 4), dtype=np.uint8)

        pal = np.array(palette)
        for y in range(h):
            for x in range(w):
                p = arr[y, x]
                # if pixel mostly transparent, set transparent
                if p[3] < 30:
                    out[y, x] = pal[-1]
                    continue
                d = np.sum((pal[:, :3] - p[:3]) ** 2, axis=1)
                idx = int(np.argmin(d[:-1]))  # exclude transparent from matching
                out[y, x] = pal[idx]

        # upscale to view size using nearest neighbor to keep hard pixels
        up = Image.fromarray(out, mode='RGBA').resize((512, 512), resample=Image.NEAREST)

        # ensure strong outline: detect edges on alpha-weighted luminance
        up_np = np.array(up.convert('RGB'))
        gray = cv2.cvtColor(up_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.dilate(edges, np.ones((2,2), np.uint8), iterations=1)
        up_np[edges != 0] = (24, 24, 24)
        return Image.fromarray(up_np)

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
        filename_styled = os.path.join(out_dir, f'rage_face_{ts}.png')
        filename_pixel = os.path.join(out_dir, f'rage_face_pixel_{ts}.png')
        styled.save(filename_styled)
        try:
            pixel = stylize_pixel_art(pil)
            pixel.save(filename_pixel)
            print('Saved:', filename_styled, filename_pixel)
        except Exception as e:
            print('Saved styled only:', filename_styled, ' (pixel art failed:', e, ')')
        return filename_styled
    else:
        print('Preview closed without saving')
        return None


if __name__ == '__main__':
    make_rage_face()
