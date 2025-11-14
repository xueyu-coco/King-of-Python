import pygame

pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King of Python - The Great Keyboard")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
BLUE = (60, 120, 255)
ORANGE = (255, 150, 50)
GREEN = (80, 200, 80)
GRAY = (150, 150, 150)
CYAN = (0, 255, 255)
PURPLE = (200, 40, 255)  # shift toward blue (less red) per user request
YELLOW = (255, 215, 0)
ICE_BLUE = (173, 216, 230)
DARK_RED = (139, 0, 0)
# Main background color — set to white per user request
BG_COLOR = (255, 255, 255)
KEY_COLOR = (220, 220, 230)
KEY_SHADOW = (100, 100, 120)
KEY_SIDE = (180, 180, 200)

# 游戏设置
FPS = 60
GRAVITY = 1.0
JUMP_POWER = -18
MOVE_SPEED = 6
ATTACK_COOLDOWN = 30
BUBBLE_SPAWN_TIME = 150
FREEZE_DURATION = 180
REVERSED_DURATION = 600
PROJECTILE_SPEED = 10

# 字体 - 使用方舟像素字体
import os
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'ark-pixel-12px-proportional-zh_cn.otf')

font_large = pygame.font.Font(FONT_PATH, 60)
font_medium = pygame.font.Font(FONT_PATH, 45)
font_small = pygame.font.Font(FONT_PATH, 30)
font_tiny = pygame.font.Font(FONT_PATH, 22)
font_bubble = pygame.font.Font(FONT_PATH, 20)
font_key = pygame.font.Font(FONT_PATH, 35)
