import os
import sys
import time
import pygame
import cv2
from PIL import Image

# Ensure repo root is on sys.path so package imports work when this file
# is executed directly (python face_detection/face_login_demo.py) from the repo root.
HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from face_detection.Face_Detection import capture_face_image, crop_to_face, circular_mask_image, ensure_outputs_dir  # noqa: E402

def capture_and_make_sprite(player_label, palette_mode='cute'):
    print(f'Please position {player_label} in front of the camera...')
    # derive a nicer display label for the capture window (show "Player 1 face" / "Player 2 face")
    if '1' in player_label:
        display_label = 'Player 1'
    elif '2' in player_label:
        display_label = 'Player 2'
    else:
        display_label = player_label

    # give the user a short pause to get ready before the detection begins
    print(f'Starting capture for {display_label} in 5 seconds...')
    time.sleep(5)
    frame, face = capture_face_image(wait_seconds=3, label=display_label)
    if face is None:
        raise RuntimeError('No face captured')
    crop = crop_to_face(frame, face, pad=0.5)
    pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    # Mirror the image horizontally so the saved avatar is a mirrored/selfie view
    pil = pil.transpose(Image.FLIP_LEFT_RIGHT)
    circ = circular_mask_image(pil)
    # Save the plain circular avatar (no stylization) so the avatar looks normal
    # Cap saved avatar size so files are moderate (not oversized)
    MAX_AVATAR = 256
    w, h = circ.size
    if max(w, h) > MAX_AVATAR:
        circ = circ.resize((MAX_AVATAR, MAX_AVATAR), resample=Image.LANCZOS)
    out_dir = ensure_outputs_dir()
    ts = int(time.time())
    avatar_path = os.path.join(out_dir, f'{player_label}_avatar_{ts}.png')
    circ.save(avatar_path)
    return avatar_path


def capture_two_and_make_sprites(label1='Face1', label2='Face2', palette_mode='cute'):
    """Capture two faces in one session and save two avatar files.
    Returns (path1, path2).
    """
    # derive nicer display labels
    if '1' in label1:
        display1 = 'Player 1'
    else:
        display1 = label1
    if '2' in label2:
        display2 = 'Player 2'
    else:
        display2 = label2

    from face_detection.Face_Detection import capture_two_faces, crop_to_face, circular_mask_image, ensure_outputs_dir  # noqa: E402

    frame, faces = capture_two_faces(wait_seconds=3, label1=display1, label2=display2)
    if not faces or len(faces) < 2:
        raise RuntimeError('Failed to detect two faces')

    out_dir = ensure_outputs_dir()
    ts = int(time.time())

    # ensure consistent ordering: left face -> player1, right face -> player2
    faces_sorted = sorted(faces, key=lambda r: r[0])
    (x1, y1, w1, h1), (x2, y2, w2, h2) = faces_sorted

    # crop and save both
    crop1 = crop_to_face(frame, (x1, y1, w1, h1), pad=0.5)
    crop2 = crop_to_face(frame, (x2, y2, w2, h2), pad=0.5)

    pil1 = Image.fromarray(cv2.cvtColor(crop1, cv2.COLOR_BGR2RGB))
    pil2 = Image.fromarray(cv2.cvtColor(crop2, cv2.COLOR_BGR2RGB))

    # Mirror both images horizontally for a selfie-like avatar
    pil1 = pil1.transpose(Image.FLIP_LEFT_RIGHT)
    pil2 = pil2.transpose(Image.FLIP_LEFT_RIGHT)

    circ1 = circular_mask_image(pil1)
    circ2 = circular_mask_image(pil2)

    p1_path = os.path.join(out_dir, f'{label1}_avatar_{ts}.png')
    p2_path = os.path.join(out_dir, f'{label2}_avatar_{ts}.png')
    circ1.save(p1_path)
    circ2.save(p2_path)

    return p1_path, p2_path


def run_login_and_demo():
    # Capture two players
    p1_sprite = capture_and_make_sprite('Face1')
    # give the user a longer pause to swap positions between captures
    time.sleep(1.5)
    p2_sprite = capture_and_make_sprite('Face2')

    print('Captured sprites:', p1_sprite, p2_sprite)

    # Simple Pygame window showing both sprites and then launching the main demo
    pygame.init()
    screen = pygame.display.set_mode((640, 360))
    pygame.display.set_caption('Face Login Demo')
    clock = pygame.time.Clock()

    img1 = pygame.image.load(p1_sprite).convert_alpha()
    img2 = pygame.image.load(p2_sprite).convert_alpha()
    # scale display sizes so portraits don't exceed screen
    MAX_DISPLAY = 180
    def scale_for_display(surf):
        w, h = surf.get_size()
        if max(w, h) > MAX_DISPLAY:
            scale = MAX_DISPLAY / max(w, h)
            return pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))
        return surf

    img1 = scale_for_display(img1)
    img2 = scale_for_display(img2)

    showing = True
    while showing:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    showing = False

        screen.fill((40, 40, 60))
        screen.blit(img1, (80, 60))
        screen.blit(img2, (360, 60))
        font = pygame.font.Font(None, 36)
        # no labels requested — just show the avatars
        screen.blit(font.render('Press SPACE to continue to demo', True, (240,240,240)), (80, 300))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    print('You can now run the main demo; portraits saved in outputs folder.')


if __name__ == '__main__':
    run_login_and_demo()
