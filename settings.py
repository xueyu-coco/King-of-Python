import pygame

pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
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
PURPLE = (160, 32, 240)
YELLOW = (255, 215, 0)
ICE_BLUE = (173, 216, 230)
DARK_RED = (139, 0, 0)
BG_COLOR = (240, 240, 250)
KEY_COLOR = (220, 220, 230)
KEY_SHADOW = (100, 100, 120)
KEY_SIDE = (180, 180, 200)

# 游戏设置
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -15
MOVE_SPEED = 5
ATTACK_COOLDOWN = 30
BUBBLE_SPAWN_TIME = 150
FREEZE_DURATION = 180
REVERSED_DURATION = 600
PROJECTILE_SPEED = 8

# 字体
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)
font_tiny = pygame.font.Font(None, 24)
font_bubble = pygame.font.Font(None, 20)
font_key = pygame.font.Font(None, 36)
