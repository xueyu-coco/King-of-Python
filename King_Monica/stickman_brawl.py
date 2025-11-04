import pygame
import sys

WIDTH, HEIGHT = 960, 540
FPS = 60

GROUND_Y = HEIGHT - 80


class Stickman:
    def __init__(self, x, color, controls):
        self.x = x
        self.y = GROUND_Y
        self.vx = 0.0
        self.vy = 0.0
        self.width = 36
        self.height = 72
        self.facing = 1
        self.on_ground = True
        self.color = color
        self.controls = controls
        self.attack_cooldown = 0.0
        self.attacking = False
        self.health = 100

    def rect(self):
        return pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height), self.width, self.height)

    def update(self, dt, keys):
        ax = 0.0
        if keys[self.controls['left']]:
            ax -= 420
            self.facing = -1
        if keys[self.controls['right']]:
            ax += 420
            self.facing = 1
        if keys[self.controls['jump']] and self.on_ground:
            self.vy = -520
            self.on_ground = False

        # movement
        self.vx += ax * dt
        self.vx = max(-420, min(420, self.vx))
        if abs(ax) < 1:
            self.vx *= 0.88
        self.x += self.vx * dt

        # gravity
        self.vy += 1500 * dt
        self.y += self.vy * dt

        # ground
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0.0
            self.on_ground = True

        # clamp
        self.x = max(40, min(WIDTH - 40, self.x))

        # cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.attacking = False

    def try_attack(self, keys):
        if keys[self.controls['attack']] and self.attack_cooldown <= 0.0:
            self.attack_cooldown = 0.48
            self.attacking = True

    def attack_hitbox(self):
        r = self.rect()
        if self.facing >= 0:
            return pygame.Rect(r.right, r.centery - 18, 48, 36)
        else:
            return pygame.Rect(r.left - 48, r.centery - 18, 48, 36)

    def draw(self, surf):
        # Minimalist stickman rendering: head, single-line torso, simple limbs
        head_radius = 10
        head_x = int(self.x)
        head_y = int(self.y - self.height + 18)

        # head (outline + fill)
        pygame.draw.circle(surf, (0, 0, 0), (head_x, head_y), head_radius)
        pygame.draw.circle(surf, (255, 255, 255), (head_x, head_y), head_radius - 2)

        # body line (neck to pelvis)
        neck_y = head_y + head_radius
        pelvis_y = int(self.y - 18)
        pygame.draw.line(surf, (0, 0, 0), (head_x, neck_y), (head_x, pelvis_y), 3)

        # arms: simple lines from shoulder point
        shoulder_y = neck_y + 6
        arm_len = 30
        # attacking extends the arm
        if self.attacking:
            arm_len = 48

        left_arm_end = (head_x - arm_len, shoulder_y)
        right_arm_end = (head_x + arm_len, shoulder_y)
        pygame.draw.line(surf, (0, 0, 0), (head_x, shoulder_y), left_arm_end, 3)
        pygame.draw.line(surf, (0, 0, 0), (head_x, shoulder_y), right_arm_end, 3)

        # legs: simple lines from pelvis to feet
        leg_offset = 12
        left_foot = (head_x - leg_offset, int(self.y))
        right_foot = (head_x + leg_offset, int(self.y))
        pygame.draw.line(surf, (0, 0, 0), (head_x, pelvis_y), left_foot, 3)
        pygame.draw.line(surf, (0, 0, 0), (head_x, pelvis_y), right_foot, 3)

        # small eyes (for expression)
        eye_off_x = 4
        eye_off_y = -2
        pygame.draw.circle(surf, (0, 0, 0), (head_x - eye_off_x, head_y + eye_off_y), 2)
        pygame.draw.circle(surf, (0, 0, 0), (head_x + eye_off_x, head_y + eye_off_y), 2)

        # if attacking, show hitbox for debug/feedback
        if self.attacking:
            hb = self.attack_hitbox()
            pygame.draw.rect(surf, (255, 60, 60), hb, 2)


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Stickman Brawl')
    clock = pygame.time.Clock()

    left_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'attack': pygame.K_f}
    right_controls = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'attack': pygame.K_l}

    p1 = Stickman(220, (245, 200, 40), left_controls)
    p2 = Stickman(740, (70, 140, 240), right_controls)

    font = pygame.font.SysFont(None, 36)

    running = True
    winner = None
    while running:
        dt = clock.tick(FPS) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        p1.update(dt, keys)
        p2.update(dt, keys)
        p1.try_attack(keys)
        p2.try_attack(keys)

        if p1.attacking and p1.attack_hitbox().colliderect(p2.rect()):
            p2.health = max(0, p2.health - 12)
        if p2.attacking and p2.attack_hitbox().colliderect(p1.rect()):
            p1.health = max(0, p1.health - 12)

        if p1.health <= 0:
            winner = 'Right Player Wins!'
            running = False
        if p2.health <= 0:
            winner = 'Left Player Wins!'
            running = False

        screen.fill((200, 220, 255))
        pygame.draw.rect(screen, (90, 60, 40), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

        ui_h = 64
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, WIDTH, ui_h))

        portrait_r = 20
        lx = 110
        rx = WIDTH - 110
        pygame.draw.circle(screen, p1.color, (lx, ui_h // 2), portrait_r)
        pygame.draw.circle(screen, (0, 0, 0), (lx, ui_h // 2), portrait_r, 2)
        pygame.draw.circle(screen, p2.color, (rx, ui_h // 2), portrait_r)
        pygame.draw.circle(screen, (0, 0, 0), (rx, ui_h // 2), portrait_r, 2)

        gap = 48
        bar_w = 300
        bar_h = 18
        left_x = lx + 30
        right_x = rx - 30 - bar_w
        if left_x + bar_w + gap > right_x:
            bar_w = max(80, (right_x - left_x - gap))
            right_x = rx - 30 - bar_w

        pygame.draw.rect(screen, (80, 80, 80), (left_x, (ui_h - bar_h)//2, bar_w, bar_h))
        pygame.draw.rect(screen, (80, 80, 80), (right_x, (ui_h - bar_h)//2, bar_w, bar_h))
        pygame.draw.rect(screen, (200, 40, 40), (left_x, (ui_h - bar_h)//2, int(bar_w * (p1.health/100)), bar_h))
        right_fill = int(bar_w * (p2.health/100))
        pygame.draw.rect(screen, (40, 120, 200), (right_x + (bar_w - right_fill), (ui_h - bar_h)//2, right_fill, bar_h))

        p1.draw(screen)
        p2.draw(screen)

        instr = font.render('Left: WASD + F   Right: Arrows + L', True, (10,10,10))
        screen.blit(instr, (20, ui_h + 8))

        pygame.display.flip()

    screen.fill((30,30,30))
    txt = font.render(winner or 'Quit', True, (255,255,255))
    txt2 = font.render('Press R to restart or Q to quit', True, (180,180,180))
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 40))
    screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, HEIGHT//2 + 10))
    pygame.display.flip()

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    run_game()
                    return
                if ev.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


if __name__ == '__main__':
    run_game()

