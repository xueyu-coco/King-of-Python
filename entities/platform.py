import pygame
from settings import *

class KeyPlatform:
    """键盘按键平台类"""
    def __init__(self, x, y, width, height, label, is_dynamic=False):
        self.x = x
        self.y = y
        self.base_y = y  # 用于动态平台
        self.width = width
        self.height = height
        self.label = label
        self.is_dynamic = is_dynamic
        self.move_direction = 1
        self.move_speed = 1
        self.move_range = 60  # 移动范围
        
    def update(self):
        """更新动态平台位置"""
        if self.is_dynamic:
            self.y += self.move_speed * self.move_direction
            
            # 到达边界时反转方向
            if self.y <= self.base_y - self.move_range:
                self.move_direction = 1
            elif self.y >= self.base_y + self.move_range:
                self.move_direction = -1
    
    def draw(self, screen):
        """绘制3D键帽效果"""
        # 绘制按键阴影（底部）
        shadow_offset = 5
        pygame.draw.rect(screen, KEY_SHADOW, 
                        (self.x + shadow_offset, self.y + shadow_offset, 
                         self.width, self.height))
        
        # 绘制按键侧面（3D效果）
        side_offset = 3
        pygame.draw.rect(screen, KEY_SIDE, 
                        (self.x, self.y + side_offset, 
                         self.width, self.height))
        
        # 绘制按键顶面
        if self.is_dynamic:
            # Shift键用特殊颜色
            key_color = (200, 220, 255)
        else:
            key_color = KEY_COLOR
            
        pygame.draw.rect(screen, key_color, 
                        (self.x, self.y, self.width, self.height))
        
        # 绘制按键边框
        pygame.draw.rect(screen, BLACK, 
                        (self.x, self.y, self.width, self.height), 2)
        
        # 绘制按键标签（字母）
        label_text = font_key.render(self.label, True, BLACK)
        label_rect = label_text.get_rect(
            center=(self.x + self.width//2, self.y + self.height//2)
        )
        screen.blit(label_text, label_rect)
        
        # 动态平台额外标识
        if self.is_dynamic:
            # 绘制小箭头指示移动
            arrow = "↕" if self.move_direction == 1 else "↕"
            arrow_text = font_tiny.render(arrow, True, BLUE)
            arrow_rect = arrow_text.get_rect(
                center=(self.x + self.width//2, self.y - 15)
            )
            screen.blit(arrow_text, arrow_rect)  