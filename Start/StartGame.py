
import pygame
from settings import *

import os


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
    # 加载背景图片（只加载一次）
    bg_path = os.path.join(os.path.dirname(__file__), '../assets/StartGamePic.png')
    bg_image = pygame.image.load(bg_path).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    running = True
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

        # 显示背景图片
        screen.blit(bg_image, (0, 0))

        # 可选：在底部显示提示文字
        font = pygame.font.SysFont(None, 36)
        sub = font.render('press space to start', True, (180, 180, 180))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()



    """Run the custom start screen. Returns 'capture' if SPACE pressed, 'skip' if S pressed."""
    # 加载背景图片（只加载一次）
    bg_path = os.path.join(os.path.dirname(__file__), '../assets/StartGamePic.png')
    bg_image = pygame.image.load(bg_path).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    running = True
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

        # 显示背景图片
        screen.blit(bg_image, (0, 0))

        # 可选：在底部显示提示文字
        font = pygame.font.SysFont(None, 36)
        sub = font.render('press space to start', True, (180, 180, 180))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()

