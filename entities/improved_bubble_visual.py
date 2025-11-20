"""改进的泡泡视觉效果 - 像素风格加强版"""
import pygame
import math
import random
from settings import font_bubble, BLACK, WHITE


class EnhancedBubble:
    """增强版泡泡 - 包含视觉效果"""
    
    def __init__(self, x, y, bubble_type='pow'):
        self.x = x
        self.y = y
        self.size = 32
        self.vel_y = 2.5
        self.type = bubble_type
        self.active = True
        self.rotation = 0
        self.pulse = 0
        
        # 颜色映射
        self.color_map = {
            'pow': (255, 150, 50),        # 橙色
            'delete': (255, 60, 60),       # 红色
            'print': (255, 215, 0),        # 黄色
            'ctrlc': (0, 255, 255),        # 青色
            'typeerror': (139, 0, 0)       # 深红
        }
        
        # 炫光颜色（基于泡泡类型）
        self.glow_colors = {
            'pow': [(255, 180, 80), (255, 150, 50), (255, 120, 20)],
            'delete': [(255, 100, 100), (255, 60, 60), (200, 0, 0)],
            'print': [(255, 235, 80), (255, 215, 0), (255, 180, 0)],
            'ctrlc': [(100, 255, 255), (0, 255, 255), (0, 200, 200)],
            'typeerror': [(200, 80, 80), (139, 0, 0), (100, 0, 0)]
        }
        
        self.color = self.color_map.get(bubble_type, (200, 200, 200))
        self.glow = self.glow_colors.get(bubble_type, [(200, 200, 200)] * 3)
    
    def update(self):
        """更新泡泡状态"""
        self.y += self.vel_y
        self.rotation = (self.rotation + 2) % 360
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        
        if self.y > pygame.display.get_surface().get_height():
            self.active = False
    
    def draw(self, screen):
        """绘制像素风格泡泡"""
        if not self.active:
            return
        
        x, y = int(self.x), int(self.y)
        
        # 计算脉冲大小
        pulse_offset = math.sin(self.pulse) * 2
        current_size = self.size + pulse_offset
        radius = int(current_size / 2)
        
        # 绘制外层炫光
        self._draw_glow(screen, x, y, radius)
        
        # 绘制主体
        self._draw_body(screen, x, y, radius)
        
        # 绘制特效
        self._draw_special_effects(screen, x, y, radius)
        
        # 绘制标签
        self._draw_label(screen, x, y)
    
    def _draw_glow(self, screen, x, y, radius):
        """绘制炫光层"""
        # 多层光晕
        for i, color in enumerate(self.glow):
            glow_radius = radius + (3 - i) * 4
            
            # 计算透明度
            alpha_val = int(100 * (1 - i / len(self.glow)))
            
            # 绘制发光圆
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, alpha_val), 
                             (glow_radius, glow_radius), glow_radius)
            
            screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
    
    def _draw_body(self, screen, x, y, radius):
        """绘制泡泡主体"""
        # 主体圆形
        pygame.draw.circle(screen, self.color, (x, y), radius)
        
        # 白色边框
        pygame.draw.circle(screen, WHITE, (x, y), radius, 3)
        
        # 像素化效果：在边缘添加小方块
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            edge_x = int(x + math.cos(rad) * radius)
            edge_y = int(y + math.sin(rad) * radius)
            pygame.draw.rect(screen, WHITE, (edge_x - 2, edge_y - 2, 4, 4))
        
        # 高光
        hl_offset = radius // 3
        hl_x = x - hl_offset
        hl_y = y - hl_offset
        
        # 渐变高光
        for i in range(8):
            hl_radius = 8 - i
            alpha = int(255 * (1 - i / 8))
            hl_color = (255, 255, 255, alpha)
            hl_surf = pygame.Surface((hl_radius * 2, hl_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(hl_surf, hl_color, (hl_radius, hl_radius), hl_radius)
            screen.blit(hl_surf, (hl_x - hl_radius, hl_y - hl_radius))
    
    def _draw_special_effects(self, screen, x, y, radius):
        """绘制特殊效果"""
        if self.type == 'ctrlc':
            # 闪电/电击效果
            if pygame.time.get_ticks() % 500 < 250:
                spark_count = 8
                for i in range(spark_count):
                    angle = (360 / spark_count) * i + (pygame.time.get_ticks() % 100) * 3
                    rad = math.radians(angle)
                    
                    spark_x = int(x + math.cos(rad) * (radius + 12))
                    spark_y = int(y + math.sin(rad) * (radius + 12))
                    
                    # 绘制闪电粒子
                    pygame.draw.circle(screen, (255, 255, 100), (spark_x, spark_y), 3)
                    pygame.draw.line(screen, (255, 255, 100),
                                   (x, y), (spark_x, spark_y), 1)
        
        elif self.type == 'typeerror':
            # 旋转警告箭头
            if pygame.time.get_ticks() % 800 < 400:
                for i, angle in enumerate([45, 135, 225, 315]):
                    rot_angle = angle + (pygame.time.get_ticks() % 360) * 2
                    rad = math.radians(rot_angle)
                    
                    arrow_x = int(x + math.cos(rad) * (radius + 14))
                    arrow_y = int(y + math.sin(rad) * (radius + 14))
                    
                    # 绘制旋转的方块
                    pygame.draw.circle(screen, (255, 100, 100), (arrow_x, arrow_y), 4)
        
        elif self.type == 'print':
            # 打印机进纸效果
            lines = int((pygame.time.get_ticks() / 100) % 4)
            for i in range(lines):
                line_y = y - radius + (i * 6)
                pygame.draw.line(screen, self.color,
                               (x - radius, line_y), (x + radius, line_y), 1)
        
        elif self.type == 'pow':
            # 爆炸星星
            star_count = 6
            for i in range(star_count):
                angle = (360 / star_count) * i
                rad = math.radians(angle)
                
                star_x = int(x + math.cos(rad) * (radius + 8))
                star_y = int(y + math.sin(rad) * (radius + 8))
                
                # 绘制小星星
                star_size = 3
                pygame.draw.polygon(screen, (255, 255, 100), [
                    (star_x, star_y - star_size),
                    (star_x + star_size, star_y),
                    (star_x, star_y + star_size),
                    (star_x - star_size, star_y)
                ])
        
        elif self.type == 'delete':
            # X 标记
            cross_size = radius + 6
            pygame.draw.line(screen, self.color,
                           (x - cross_size, y - cross_size),
                           (x + cross_size, y + cross_size), 2)
            pygame.draw.line(screen, self.color,
                           (x + cross_size, y - cross_size),
                           (x - cross_size, y + cross_size), 2)
    
    def _draw_label(self, screen, x, y):
        """绘制泡泡标签"""
        label_map = {
            'pow': 'pow()',
            'delete': 'delete',
            'print': 'print',
            'ctrlc': 'Ctrl+C',
            'typeerror': 'TypeError'
        }
        
        if self.type in label_map:
            label = label_map[self.type]
            text = font_bubble.render(label, True, BLACK)
            
            # 添加白色阴影以增强可读性
            shadow = font_bubble.render(label, True, WHITE)
            for offset_x, offset_y in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                text_rect = shadow.get_rect(center=(x + offset_x, y + offset_y))
                screen.blit(shadow, text_rect)
            
            # 主文字
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)
    
    def check_collision(self, player):
        """检查与玩家的碰撞"""
        dist = math.sqrt((self.x - (player.x + player.width // 2)) ** 2 +
                        (self.y - (player.y + player.height // 2)) ** 2)
        return dist < self.size + player.width // 2