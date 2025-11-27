import os
import sys

import cv2
import pygame

# Make sure the repository root is on sys.path so we can import project modules.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from settings import *


def draw_hearts(surface, x, y, count, spacing=28, size=18, color=(255, 200, 255)):
    for i in range(count):
        cx = x + i * spacing
        # draw a simple heart using two circles and a triangle-ish polygon
        left = (cx - size//4, y)
        right = (cx + size//4, y)
        top = (cx, y - size//3)
        pygame.draw.circle(surface, color, left, size//3)
        pygame.draw.circle(surface, color, right, size//3)
        points = [(cx - size//2, y), (cx + size//2, y), (cx, y + size//2)]
        pygame.draw.polygon(surface, color, points)


def run_start(screen, clock):
    """Run the custom start screen. Returns 'capture' if SPACE pressed, 'skip' if S pressed."""
    assets_dir = os.path.join(os.path.dirname(__file__), '../assets')
    video_path = os.path.join(assets_dir, 'StartGameVideo.mp4')
    image_path = os.path.join(assets_dir, 'StartGamePic.png')

    # Try to open the intro video; fall back to the static image on failure.
    video_cap = None
    use_video = False
    try:
        if os.path.exists(video_path):
            video_cap = cv2.VideoCapture(video_path)
            if video_cap.isOpened():
                use_video = True
            else:
                video_cap.release()
                video_cap = None
    except Exception:
        if video_cap is not None:
            video_cap.release()

    bg_image = None
    if not use_video:
        bg_image = pygame.image.load(image_path).convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    prompt_font = pygame.font.SysFont(None, 36)

    running = True
    try:
        while running:
            clock.tick(FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_s:
                        return 'skip'
                    if ev.key == pygame.K_SPACE:
                        return 'capture'

            if use_video and video_cap is not None:
                ret, frame = video_cap.read()
                if not ret:
                    # Loop the video by restarting from first frame.
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.image.frombuffer(frame.tobytes(), (WIDTH, HEIGHT), 'RGB')
                screen.blit(frame_surface, (0, 0))
            else:
                screen.blit(bg_image, (0, 0))

            # 可选：在底部显示提示文字
            sub = prompt_font.render('press space to start', True, (180, 180, 180))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT - 60))

            pygame.display.flip()
    finally:
        if video_cap is not None:
            video_cap.release()


if __name__ == "__main__":
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("King of Python - Start")
        clock = pygame.time.Clock()
        run_start(screen, clock)
    finally:
        pygame.quit()

