import os
import sys
import time
import pygame
import cv2
from PIL import Image

# Ensure repo root is on sys.path so package imports work when this file
# is executed directly (python King_Monica/face_login_demo.py) from the repo root.
HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from King_Monica.Face_Detection import capture_face_image, crop_to_face, circular_mask_image, ensure_outputs_dir  # noqa: E402


def capture_and_make_sprite(player_label, palette_mode='cute'):
    print(f'Please position {player_label} in front of the camera...')
    frame, face = capture_face_image(wait_seconds=3)
    if face is None:
        raise RuntimeError('No face captured')
    crop = crop_to_face(frame, face, pad=0.5)
    pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
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
