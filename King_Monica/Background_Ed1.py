import pygame
import random
import math

# 初始化Pygame
pygame.init()

# 设置窗口尺寸
cw, ch = 1200, 800
screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
pygame.display.set_caption("Matrix Digital Rain")

# 颜色定义
GREEN = (0, 180, 0)
BRIGHT_GREEN = (120, 220, 120)
DARK_GREEN = (0, 80, 0)
BLACK = (0, 0, 0)

# 字符数组 - 包含字母和数字，类似图片中的字符
char_arr = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# 流设置
max_char_count = 80
char_streams = []
font_size = 20
stream_speed_min = 2
stream_speed_max = 8

# 计算列数
columns = cw // font_size

class CharStream:
    def __init__(self, column):
        self.column = column
        self.x = column * font_size
        self.chars = []
        self.speed = random.uniform(stream_speed_min, stream_speed_max)
        self.stream_length = random.randint(8, 25)
        self.head_char_index = 0
        self.last_char_time = 0
        self.char_interval = 100  # 毫秒
        self.generate_initial_chars()
    
    def generate_initial_chars(self):
        # 创建初始字符，从屏幕上方开始
        for i in range(self.stream_length):
            char = {
                'value': random.choice(char_arr),
                'y': -i * font_size,  # 从屏幕外开始
                'bright': False
            }
            # no special bright head character
            self.chars.append(char)
    
    def update(self, current_time):
        # 更新字符位置
        for char in self.chars:
            char['y'] += self.speed
        
        # 移除超出屏幕的字符并添加新字符
        if self.chars and self.chars[0]['y'] > ch:
            self.chars.pop(0)
            new_char = {
                'value': random.choice(char_arr),
                'y': self.chars[-1]['y'] - font_size if self.chars else -font_size,
                'bright': False
            }
            self.chars.append(new_char)
        
        # no blinking bright character logic
    
    def draw(self, screen, font):
        for i, char in enumerate(self.chars):
            # 字符颜色渐变 - 头部字符最亮，尾部渐暗
            if char['bright']:
                color = BRIGHT_GREEN
                # make the blinking bright character slightly more transparent than before
                alpha = 150
            else:
                # 根据在流中的位置计算亮度，顶部字符更亮，减少减淡系数以整体提亮
                raw = 1.0 - (i / self.stream_length)
                brightness = max(0.2, 1.0 * raw)
                color = (
                    int(GREEN[0] * brightness),
                    int(GREEN[1] * brightness),
                    int(GREEN[2] * brightness)
                )
                # use 90% overall alpha to make characters brighter
                # 255 * 0.90 = 229
                alpha = int(229 * brightness)

            # 绘制字符（使用 alpha 调低亮度）
            if 0 <= char['y'] <= ch:
                text_surface = font.render(char['value'], True, color).convert_alpha()
                # apply alpha to tone down brightness
                text_surface.set_alpha(alpha)
                screen.blit(text_surface, (self.x, char['y']))

def create_streams():
    """创建初始的数字雨流"""
    global char_streams
    char_streams = []
    
    # 随机选择一些列来创建流
    available_columns = list(range(columns))
    random.shuffle(available_columns)
    
    num_streams = min(max_char_count, len(available_columns))
    for i in range(num_streams):
        col = available_columns[i]
        stream = CharStream(col)
        char_streams.append(stream)

def handle_resize(event):
    global cw, ch, columns
    cw, ch = event.w, event.h
    screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
    columns = cw // font_size
    create_streams()

def main():
    global char_streams
    
    # 创建字体
    font = pygame.font.SysFont('couriernew', font_size, bold=True)
    
    # 创建初始流
    create_streams()
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill(BLACK)
        
        # 更新和绘制所有流
        for stream in char_streams:
            stream.update(current_time)
            stream.draw(screen, font)
        
        # 随机添加新流
        if len(char_streams) < max_char_count and random.random() < 0.02:
            available_columns = set(range(columns)) - set(stream.column for stream in char_streams)
            if available_columns:
                col = random.choice(list(available_columns))
                new_stream = CharStream(col)
                char_streams.append(new_stream)
        
        # 随机移除一些流以创建动态效果
        if char_streams and random.random() < 0.01:
            char_streams.pop(random.randint(0, len(char_streams) - 1))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()