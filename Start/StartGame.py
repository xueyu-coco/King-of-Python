import pygame
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
    running = True
    selected = 0
    menu = ['PLAY GAME', 'START', 'PAUSE', 'CONTINUE']

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

        # background purple frame and black inner
        screen.fill((180, 120, 220))
        inner_rect = pygame.Rect(40, 40, WIDTH - 80, HEIGHT - 120)
        pygame.draw.rect(screen, BLACK, inner_rect)

        # top hearts
        draw_hearts(screen, inner_rect.left + 80, inner_rect.top + 20, 10, spacing=40, size=20, color=(240, 200, 255))

        # three round emoji placeholders at top center - 向下移动
        center_x = inner_rect.centerx
        yy = inner_rect.top + 120  # 从 80 改为 120，向下移动 40 像素
        for i, col in enumerate([(255, 230, 120), (255, 120, 120), (255, 230, 120)]):
            cx = center_x + (i - 1) * 120
            pygame.draw.circle(screen, col, (cx, yy), 40)
            pygame.draw.circle(screen, (160, 80, 200), (cx, yy), 44, 4)

        # decorative items: gem left, hammer right
        pygame.draw.polygon(screen, (160, 80, 200), [(inner_rect.left + 60, inner_rect.bottom - 180), (inner_rect.left + 110, inner_rect.bottom - 220), (inner_rect.left + 90, inner_rect.bottom - 140)])
        pygame.draw.rect(screen, (160, 80, 200), (inner_rect.right - 100, inner_rect.top + 60, 24, 80))  # 从 -140 改为 -100，向右移动 40 像素

        # menu text in center
        title = font_large.render('King of Python', True, (255, 240, 255))
        screen.blit(title, (inner_rect.centerx - title.get_width()//2, inner_rect.centery - 100))  # 从 -60 改为 -100，向上移动 40 像素

        # menu lines - 往下移动
        items = ['START']
        y0 = inner_rect.centery + 40  # 从 -10 改为 +40，向下移动 50 像素
        for i, text in enumerate(['START', 'PAUSE', 'CONTINUE']):
            color = (180, 250, 250) if i == 0 else (200, 170, 240)
            t = font_medium.render(text, True, color)
            screen.blit(t, (inner_rect.centerx - t.get_width()//2, y0 + i * 48))

        # bottom-left small avatar and pac-man
        pygame.draw.circle(screen, (255, 230, 120), (inner_rect.left + 40, inner_rect.bottom - 30), 18)
        pygame.draw.polygon(screen, (255, 220, 80), [(inner_rect.left + 80, inner_rect.bottom - 40), (inner_rect.left + 100, inner_rect.bottom - 40), (inner_rect.left + 90, inner_rect.bottom - 20)])

        # bottom-right BE HAPPY - 向上移动，顶部与左下角黄色圆形顶部对齐
        be = font_medium.render('BE HAPPY', True, (160, 255, 220))
        # 左下角黄色圆形顶部位置: inner_rect.bottom - 30 - 18 = inner_rect.bottom - 48
        # BE HAPPY 文字顶部也应该在 inner_rect.bottom - 48
        be_y = inner_rect.bottom - 48  # 对齐到左下角圆形顶部
        screen.blit(be, (inner_rect.right - be.get_width() - 20, be_y))

        # instruction
        sub = font_tiny.render('Press SPACE to capture faces, S to skip and start', True, (220, 220, 240))
        screen.blit(sub, (inner_rect.centerx - sub.get_width()//2, inner_rect.bottom - 80))

        pygame.display.flip()

