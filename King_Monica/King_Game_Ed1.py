import pygame
import random
import sys
 

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('King Monica - Click the Code Bubbles')
clock = pygame.time.Clock()

# Fonts
BASE_FONT_SIZE = 18
FONT = pygame.font.SysFont('consolas', BASE_FONT_SIZE)

def make_font_cache(min_size=12, max_size=28):
    cache = {}
    for s in range(min_size, max_size + 1, 2):
        cache[s] = pygame.font.SysFont('consolas', s)
    return cache

FONT_CACHE = make_font_cache(12, 28)


class RollingCode:
    """Simple vertical rolling code background like a matrix/code rain."""
    def __init__(self, width, height, font_size=BASE_FONT_SIZE, speed=160, density=3):
        # density = number of characters to render per column at a time
        self.width = width
        self.height = height
        self.font_size = font_size
        # Use the smallest font cell as column width to allow variable sizes inside
        self.cell_width = min(FONT_CACHE.keys())
        self.cols = width // self.cell_width
        self.speed = speed
        self.density = density
        self.drops = [random.randint(-height, 0) for _ in range(self.cols)]
        # use only binary digits for the matrix effect
        self.chars = ['0', '1']
        # each column has a current trailing length which grows every time the column resets
        self.lengths = [random.randint(3, 6) for _ in range(self.cols)]
        # assign a fixed font size for each column so group sizes stay consistent
        self.col_font_sizes = [random.choice(list(FONT_CACHE.keys())) for _ in range(self.cols)]
        # pre-generate stable character buffers per column to avoid flicker
        self.col_buffers = []
        for i in range(self.cols):
            buf = [random.choice(self.chars) for _ in range(self.lengths[i] + 20)]
            self.col_buffers.append(buf)

    def update(self, dt):
        for i in range(self.cols):
            self.drops[i] += self.speed * dt
            if self.drops[i] > self.height + random.randint(0, 100):
                # column wrapped; increase its trailing group length slightly
                self.drops[i] = random.randint(-100, 0)
                # increase length and extend buffer so new characters are appended
                self.lengths[i] = min(self.lengths[i] + 1, 40)
                # append new random chars to the buffer to match increased length
                extra = [random.choice(self.chars) for _ in range(5)]
                self.col_buffers[i].extend(extra)

    def draw(self, surface):
        for i, drop in enumerate(self.drops):
            x = i * self.cell_width
            # render multiple characters per column for density
            # draw a trailing group of length self.lengths[i], but cap visually by density*4 for performance
            draw_len = min(self.lengths[i], max(self.density * 2, 8))
            for j in range(draw_len):
                y = int(drop - j * self.font_size)
                # pick a stable character from the column buffer; wrap index
                buf = self.col_buffers[i]
                idx = (j + int(drop // self.font_size)) % len(buf)
                char = buf[idx]
                # compute fade so leading char is brightest
                fade = max(0, 255 - int((j / (draw_len if draw_len>0 else 1)) * 220))
                # use fade as green channel for simple brightness effect
                color = (0, fade, 70)
                # use the fixed font size for this column
                f = FONT_CACHE[self.col_font_sizes[i]]
                text = f.render(char, True, color)
                # center the character within the cell
                tx = x + (self.cell_width - text.get_width()) // 2
                ty = y % (self.height + self.font_size) - self.font_size
                surface.blit(text, (tx, ty))


class Bubble:
    def __init__(self, x, y, text, radius=40):
        self.x = x
        self.y = y
        self.text = text
        self.radius = radius
        self.color = (100, 150, 255)
        self.clicked = False
        self.effect_progress = 0.0

    def draw(self, surface):
        # draw bubble
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # draw text
        txt = FONT.render(self.text, True, (0, 0, 0))
        rect = txt.get_rect(center=(self.x, self.y))
        surface.blit(txt, rect)

        # draw effect if clicked
        if self.clicked:
            alpha = max(0, 255 - int(self.effect_progress * 255))
            s = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (self.radius*2, self.radius*2), int(self.radius*2 * self.effect_progress))
            surface.blit(s, (self.x - self.radius*2, self.y - self.radius*2))

    def update(self, dt):
        if self.clicked:
            self.effect_progress += dt * 1.5
            if self.effect_progress >= 1.0:
                self.clicked = False
                self.effect_progress = 0.0

    def is_point_inside(self, px, py):
        return (px - self.x) ** 2 + (py - self.y) ** 2 <= self.radius ** 2


def spawn_bubble():
    x = random.randint(60, WIDTH - 60)
    y = random.randint(80, HEIGHT - 80)
    # a short command/text inside the bubble
    cmds = ['ls', 'git pull', 'python', 'pip install', 'def func', 'print()', 'import', 'for i in range']
    return Bubble(x, y, random.choice(cmds), radius=random.randint(30, 50))


def main():
    # denser rolling code: smaller font_size, faster speed, higher density
    rolling = RollingCode(WIDTH, HEIGHT, font_size=12, speed=160, density=4)
    bubbles = [spawn_bubble() for _ in range(6)]
    spawn_timer = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for b in bubbles:
                    if b.is_point_inside(mx, my):
                        b.clicked = True
                        b.effect_progress = 0.0
                        # change color and play a tiny pop effect
                        b.color = (255, 200, 80)

        # update
        rolling.update(dt)
        for b in bubbles:
            b.update(dt)

        spawn_timer += dt
        if spawn_timer > 2.0:
            # occasionally add or replace a bubble
            if len(bubbles) < 8 and random.random() < 0.6:
                bubbles.append(spawn_bubble())
            else:
                bubbles[random.randrange(len(bubbles))] = spawn_bubble()
            spawn_timer = 0.0

        # draw
        screen.fill((0, 0, 0))
        rolling.draw(screen)

        # translucent overlay to darken the code background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        for b in bubbles:
            b.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
