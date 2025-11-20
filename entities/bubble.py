import pygame
import math
from settings import *

class Bubble:
    def __init__(self, x, y, bubble_type='pow'):
        self.x = x
        self.y = y
        self.size = 32
        self.vel_y = 2.5
        self.type = bubble_type
        self.active = True
        
        if self.type == 'pow':
            self.color = ORANGE
        elif self.type == 'delete':
            self.color = RED
        elif self.type == 'print':
            self.color = YELLOW
        elif self.type == 'super':
            self.color = (200, 100, 255)  # 紫色
        elif self.type == 'ctrlc':
            self.color = CYAN
        elif self.type == 'typeerror':
            self.color = DARK_RED
        else:
            self.color = GRAY
        
    def update(self):
        self.y += self.vel_y
        if self.y > HEIGHT:
            self.active = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
        
        text_color = BLACK
        
        if self.type == 'pow':
            label = 'pow()'
        elif self.type == 'delete':
            label = 'delete'
        elif self.type == 'print':
            label = 'print'
        elif self.type == 'super':
            label = 'super()'
        elif self.type == 'ctrlc':
            label = 'Ctrl+C'
        elif self.type == 'typeerror':
            label = 'TypeError'
        else:
            label = ''

        if label:
            text = font_bubble.render(label, True, text_color)
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(text, text_rect)
        
        if self.type == 'ctrlc':
            if pygame.time.get_ticks() % 500 < 250:
                for angle in range(0, 360, 90):
                    rad = math.radians(angle)
                    spark_x = int(self.x + math.cos(rad) * (self.size + 5))
                    spark_y = int(self.y + math.sin(rad) * (self.size + 5))
                    pygame.draw.circle(screen, WHITE, (spark_x, spark_y), 3)
        
        # super()泡泡的星星特效
        if self.type == 'super':
            star_count = 6
            for i in range(star_count):
                angle = (360 / star_count) * i + (pygame.time.get_ticks() % 360) * 2
                rad = math.radians(angle)
                star_x = int(self.x + math.cos(rad) * (self.size + 8))
                star_y = int(self.y + math.sin(rad) * (self.size + 8))
                pygame.draw.circle(screen, (255, 215, 0), (star_x, star_y), 3)
        
        # TypeError泡泡的混乱特效
        if self.type == 'typeerror':
            if pygame.time.get_ticks() % 400 < 200:
                # 绘制旋转的箭头
                for angle in [45, 135, 225, 315]:
                    rad = math.radians(angle)
                    arrow_x = int(self.x + math.cos(rad) * (self.size + 8))
                    arrow_y = int(self.y + math.sin(rad) * (self.size + 8))
                    pygame.draw.circle(screen, DARK_RED, (arrow_x, arrow_y), 3)
    
    def check_collision(self, player):
        dist = math.sqrt((self.x - (player.x + player.width//2))**2 + 
                        (self.y - (player.y + player.height//2))**2)
        return dist < self.size + player.width//2