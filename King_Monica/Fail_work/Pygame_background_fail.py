import pygame
import random

# Pygame Matrix-style background with optional image and resizable window

def run_matrix_background():
    pygame.init()

    # initial window size
    cw, ch = 1280, 720
    screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
    pygame.display.set_caption("Matrix Rain Background")
    clock = pygame.time.Clock()

    # try loading a background image in the project root (optional)
    bg_image = None
    try:
        bg_image = pygame.image.load('IMG_0992.JPG')
    except Exception:
        bg_image = None

    # configuration
    char_arr = list("01")
    max_char_count = 150
    char_stream_arr = []
    font_size = 15
    # visual tuning
    trail_alpha = 28  # lower = longer trails
    leader_glow_times = 3

    # frame where the matrix rain will appear (can be adjusted)
    frame_x = 45
    frame_y = 78
    frame_width = 1280 - 2 * frame_x
    frame_height = 560

    # compute columns based on minimal cell width
    max_columns = frame_width // font_size

    frames = 0
import pygame
import random

# Pygame Matrix-style background with optional image and resizable window

def run_matrix_background():
    pygame.init()

    # initial window size
    cw, ch = 1280, 720
    screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
    pygame.display.set_caption("Matrix Rain Background")
    clock = pygame.time.Clock()

    # try loading a background image in the project root (optional)
    bg_image = None
    try:
        bg_image = pygame.image.load('IMG_0992.JPG')
    except Exception:
        bg_image = None

    # configuration
    char_arr = list("01")
    max_char_count = 100  # 减少最大字符数量以降低密度
    char_stream_arr = []
    font_size = 15

    # 定义字符应该出现的框架
    frame_x = 45
    frame_y = 78
    frame_width = 1428
    frame_height = 650

    max_columns = frame_width // font_size

    frames = 0

    class FallingChar:
        def __init__(self, x, y, speed):
            self.x = x
            self.y = y
            self.speed = speed
            self.value = self.get_random_char()
            self.font = pygame.font.SysFont('Arial', font_size)

        def get_random_char(self):
            return random.choice(char_arr)

        def draw(self, screen):
            # 随机改变字符
            if random.random() > 0.98:  # 调整概率以控制变化频率
                self.value = self.get_random_char()

            # 创建文本表面
            text_surface = self.font.render(self.value, True, (0, 255, 0))
            
            # 在Pygame中模拟发光效果比较复杂，这里我们使用简单的文本绘制
            screen.blit(text_surface, (self.x, self.y))
            
            self.y += self.speed

            if self.y > frame_y + frame_height:
                self.y = frame_y
                self.value = self.get_random_char()  # 重置位置时更新字符

    class CharStream:
        def __init__(self, x):
            self.chars = []
            self.speed = (random.random() * font_size * 0.5) / 5 + (font_size * 0.5) / 5
            self.generate_stream(x)

        def generate_stream(self, x):
            stream_length = random.randint(5, 15)  # 每个流有5到15个字符
            for i in range(stream_length):
                y = frame_y - (font_size * i)
                char = FallingChar(x, y, self.speed)
                self.chars.append(char)

        def draw(self, screen):
            for char in self.chars:
                char.draw(screen)

    def handle_resize(event):
        nonlocal cw, ch, max_columns, bg_image
        cw, ch = event.w, event.h
        screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
        max_columns = frame_width // font_size
        
        if bg_image:
            bg_image = pygame.transform.scale(bg_image, (cw, ch))

    def update():
        nonlocal frames, char_stream_arr
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event)
        
        # 添加新的字符流
        if len(char_stream_arr) < max_char_count and frames % 50 == 0:
            x = random.randint(0, max_columns - 1) * font_size + frame_x
            char_stream = CharStream(x)
            char_stream_arr.append(char_stream)

        # 绘制背景图像
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # 在框架内绘制半透明矩形
        overlay = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 13))  # 半透明黑色 (0,0,0,0.05*255≈13)
        screen.blit(overlay, (frame_x, frame_y))

        # 绘制所有字符流
        for stream in char_stream_arr:
            stream.draw(screen)

        pygame.display.flip()
        
        frames += 1
        return True

    # 主循环
    running = True
    clock = pygame.time.Clock()

    while running:
        running = update()
        clock.tick(60)  # 限制帧率为60FPS

    pygame.quit()


if __name__ == '__main__':
    run_matrix_background()

