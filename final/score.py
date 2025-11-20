import pygame
import time
import math
import random
from settings import WIDTH, HEIGHT, KEY_SIDE, KEY_COLOR, KEY_SHADOW, ORANGE, YELLOW, BLACK, font_small, font_medium, CYAN, FPS


def play_score_animation(screen, winner, loser, winner_avatar=None):
    # --- UI装饰函数 ---
    def draw_hearts(surface, x, y, count, spacing=28, size=18, color=(255, 200, 255)):
        for i in range(count):
            cx = x + i * spacing
            left = (cx - size//4, y)
            right = (cx + size//4, y)
            top = (cx, y - size//3)
            pygame.draw.circle(surface, color, left, size//3)
            pygame.draw.circle(surface, color, right, size//3)
            points = [(cx - size//2, y), (cx + size//2, y), (cx, y + size//2)]
            pygame.draw.polygon(surface, color, points)

    def draw_score_ui(surface):
        # 紫色外框和黑色内框
        surface.fill((180, 120, 220))
        inner_rect = pygame.Rect(40, 40, WIDTH - 80, HEIGHT - 120)
        pygame.draw.rect(surface, BLACK, inner_rect)
        # 顶部 hearts
        draw_hearts(surface, inner_rect.left + 80, inner_rect.top + 20, 10, spacing=40, size=20, color=(240, 200, 255))
        # 三个emoji圆形
        center_x = inner_rect.centerx
        yy = inner_rect.top + 120
        for i, col in enumerate([(255, 230, 120), (255, 120, 120), (255, 230, 120)]):
            cx = center_x + (i - 1) * 120
            pygame.draw.circle(surface, col, (cx, yy), 40)
            pygame.draw.circle(surface, (160, 80, 200), (cx, yy), 44, 4)
        # 左下角小圆和pac-man
        pygame.draw.circle(surface, (255, 230, 120), (inner_rect.left + 40, inner_rect.bottom - 30), 18)
        pygame.draw.polygon(surface, (255, 220, 80), [(inner_rect.left + 80, inner_rect.bottom - 40), (inner_rect.left + 100, inner_rect.bottom - 40), (inner_rect.left + 90, inner_rect.bottom - 20)])
        # 右下角BE HAPPY
        be = font_medium.render('BE HAPPY', True, (160, 255, 220))
        be_y = inner_rect.bottom - 48
        surface.blit(be, (inner_rect.right - be.get_width() - 20, be_y))
        # 底部说明文字
        sub = font_small.render('Press SPACE to continue', True, (220, 220, 240))
        surface.blit(sub, (inner_rect.centerx - sub.get_width()//2, inner_rect.bottom - 80))
    """Play a short ending animation: winner walks to a computer, sits, and wears a crown.

    Args:
        screen: pygame display surface
        winner: Player object who won
        loser: Player object who lost (may be used for camera framing)
        winner_avatar: Optional surface to show as avatar during the sequence
    """
    clock = pygame.time.Clock()

    # (No special background) use normal BG_COLOR
    from settings import BG_COLOR

    # Setup simple scene positions (computer centered on screen)
    comp_w = 240
    comp_h = 140
    # center monitor in the middle of the screen
    comp_x = WIDTH // 2
    comp_y = HEIGHT // 2 + 80  # slightly lower than exact center so characters sit comfortably
    monitor_rect = pygame.Rect(comp_x - comp_w // 2, comp_y - comp_h // 2 - 20, comp_w, comp_h)
    chair_x = comp_x - 40
    chair_y = monitor_rect.bottom + 6

    crown = None
    try:
        crown = pygame.image.load(pygame.compat.get_resource('crown.png'))
    except Exception:
        # fallback: draw a simple crown
        crown = None

    # Determine target x for winner to walk to (center of computer)
    target_x = comp_x - winner.width // 2
    walking = True
    sit_timer = 0
    crown_timer = 0
    # Prepare jump animation params
    jump_phase = 0.0
    jump_speed = 0.18
    jump_height = 40

    # tears for loser
    tears = []

    # Freeze both players movement for the animation
    winner.vel_x = 0
    winner.vel_y = 0
    loser.vel_x = 0
    loser.vel_y = 0

    # Place loser initially to the left of the monitor (will be updated each frame)
    loser_target_x = monitor_rect.left - 120
    loser.x = loser_target_x
    loser.y = monitor_rect.bottom - loser.height + 20

    # Walk loop: move winner toward target_x
    for frame in range(FPS * 6):  # up to 6 seconds
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return

        # move winner toward target
        if walking:
            if abs(winner.x - target_x) > 4:
                step = 3 if winner.x < target_x else -3
                winner.x += step
                winner.facing_right = True if step > 0 else False
            else:
                walking = False
                sit_timer = FPS * 1  # 1 second to sit

        elif sit_timer > 0:
            # small sitting animation: lower y a bit
            winner.y += (chair_y - winner.y) * 0.2
            sit_timer -= 1
            if sit_timer <= 0:
                crown_timer = FPS * 2  # 2 seconds until crown appears

        elif crown_timer > 0:
            crown_timer -= 1


        # 先画UI装饰
        draw_score_ui(screen)

        # 再画原有胜利场景（电脑、椅子、角色等）
        # draw computer (base + monitor)
        base_h = 12
        base_rect = pygame.Rect(monitor_rect.left, monitor_rect.bottom + 6, comp_w, base_h)
        pygame.draw.rect(screen, KEY_SIDE, base_rect)
        pygame.draw.rect(screen, KEY_COLOR, monitor_rect)
        pygame.draw.rect(screen, KEY_SHADOW, monitor_rect, 3)

        # place big winner text on monitor
        vt = font_medium.render("VICTORY", True, ORANGE)
        vt_rect = vt.get_rect(center=(monitor_rect.centerx, monitor_rect.centery - 18))
        screen.blit(vt, vt_rect)

        # draw chair (decorative) under the monitor area
        pygame.draw.rect(screen, KEY_SIDE, (chair_x, chair_y, 50, 10))
        pygame.draw.rect(screen, KEY_COLOR, (chair_x, chair_y - 30, 50, 30))

        # draw loser near the computer (to the left)
        loser_target_x = monitor_rect.left - 120
        loser.x = loser_target_x
        loser.y = monitor_rect.bottom - loser.height + 20
        loser.draw(screen)

        # draw winner (on top of monitor, jumping)
        if not walking:
            jump_phase += jump_speed
            offset = -int(abs(math.sin(jump_phase)) * jump_height)
            base_y = monitor_rect.top - winner.height + 6
            winner.y = base_y + offset
        winner.x = int(winner.x)
        winner.draw(screen)

        # draw avatar above winner if provided
        if winner_avatar:
            aw = winner_avatar.get_width()
            ah = winner_avatar.get_height()
            screen.blit(winner_avatar, (int(winner.x + winner.width//2 - aw//2), int(winner.y - ah - 6)))

        # crown appears after crown_timer has started counting down
        if crown_timer > 0 or (not walking and sit_timer <= 0):
            cx = int(winner.x + winner.width//2)
            cy = int(winner.y - 22)
            if crown is not None:
                cw, ch = crown.get_size()
                crown_s = pygame.transform.smoothscale(crown, (int(winner.width * 1.2), int(ch * (winner.width * 1.2) / cw)))
                screen.blit(crown_s, (cx - crown_s.get_width()//2, cy - crown_s.get_height()//2))
            else:
                points = [(cx - 18, cy + 12), (cx - 12, cy - 6), (cx - 4, cy + 8), (cx + 4, cy - 6), (cx + 12, cy + 12)]
                pygame.draw.polygon(screen, ORANGE, points)
                pygame.draw.polygon(screen, YELLOW, points, 2)

        # overlay small caption
        sub_text = font_small.render("The King sits at his throne", True, BLACK)
        screen.blit(sub_text, (50, 100))

        # draw tears for loser
        if random.random() < 0.12:
            eye_x = int(loser.x + loser.width * 0.5)
            eye_y = int(loser.y + 16)
            tears.append({'x': eye_x + random.randint(-6, 6), 'y': eye_y, 'vy': 2 + random.random()*2})

        for t in tears[:]:
            pygame.draw.circle(screen, CYAN, (int(t['x']), int(t['y'])), 3)
            t['y'] += t['vy']
            t['vy'] += 0.12
            if t['y'] > HEIGHT:
                tears.remove(t)

        pygame.display.flip()

        # early exit when crown animation done
        if not walking and sit_timer <= 0 and crown_timer <= 0:
            # leave the final frame for a short time
            time.sleep(1.2)
            break

    # small pause at end
    time.sleep(0.6)
