"""像素风格视觉效果系统 - 为游戏添加炫光和像素美学"""
import pygame
import math
import random
import numpy as np


class PixelGlowEffect:
    """像素炫光效果 - 为元素周围添加彩色光晕"""
    
    def __init__(self, base_color, glow_colors=None, glow_size=16):
        """
        Args:
            base_color: 基础颜色 (r, g, b)
            glow_colors: 光晕颜色列表，默认使用渐变紫色
            glow_size: 光晕大小（像素）
        """
        self.base_color = base_color
        self.glow_size = glow_size
        
        # 默认炫光颜色：从深紫到浅紫的渐变
        if glow_colors is None:
            self.glow_colors = [
                (100, 50, 200, 255),    # 深紫
                (150, 100, 255, 100),   # 中紫
                (200, 150, 255, 50),    # 浅紫
                (220, 180, 255, 20),    # 更浅
            ]
        else:
            self.glow_colors = glow_colors
    
    def draw_glow(self, surface, rect, intensity=1.0):
        """在矩形周围绘制炫光
        
        Args:
            surface: 目标表面
            rect: pygame.Rect 对象
            intensity: 强度倍数 (0.0-1.0+)
        """
        # 创建临时表面用于绘制光晕
        glow_surf = pygame.Surface(
            (rect.width + self.glow_size * 4, rect.height + self.glow_size * 4),
            pygame.SRCALPHA
        )
        
        # 绘制多层光晕（从外到内）
        center_x = glow_surf.get_width() // 2
        center_y = glow_surf.get_height() // 2
        
        for i, color in enumerate(self.glow_colors):
            # 计算这一层的大小
            layer_size = self.glow_size - (i * self.glow_size // len(self.glow_colors))
            if layer_size <= 0:
                break
            
            # 调整透明度
            r, g, b, a = color
            adjusted_alpha = int(a * intensity * (1.0 - i / len(self.glow_colors)))
            
            # 绘制发光圆角矩形
            glow_rect = pygame.Rect(
                center_x - (rect.width // 2 + layer_size),
                center_y - (rect.height // 2 + layer_size),
                rect.width + layer_size * 2,
                rect.height + layer_size * 2
            )
            
            glow_color = (r, g, b, adjusted_alpha)
            pygame.draw.rect(glow_surf, glow_color, glow_rect, border_radius=8)
        
        # 将光晕绘制到主表面
        glow_rect = glow_surf.get_rect(center=rect.center)
        surface.blit(glow_surf, glow_rect)


class PixelParticleSystem:
    """像素粒子系统 - 创建炫光粒子效果"""
    
    def __init__(self):
        self.particles = []
    
    def emit_burst(self, x, y, color, count=8, speed_range=(1, 4), lifetime=30):
        """在某处发射粒子爆炸
        
        Args:
            x, y: 发射位置
            color: 粒子颜色 (r, g, b)
            count: 粒子数量
            speed_range: 速度范围 (min, max)
            lifetime: 粒子生命周期（帧数）
        """
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            particle = {
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': color,
                'size': random.randint(2, 4)
            }
            self.particles.append(particle)
    
    def update(self):
        """更新所有粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.3  # 重力
            p['lifetime'] -= 1
            
            if p['lifetime'] <= 0:
                self.particles.remove(p)
    
    def draw(self, surface):
        """绘制所有粒子"""
        for p in self.particles:
            # 根据生命周期计算透明度
            alpha = int(255 * (p['lifetime'] / p['max_lifetime']))
            
            # 绘制粒子（小方块）
            color = p['color']
            pygame.draw.rect(surface, color, 
                           (int(p['x']), int(p['y']), p['size'], p['size']))


class PixelBubbleRenderer:
    """像素风格泡泡渲染器"""
    
    @staticmethod
    def draw_bubble(screen, bubble, particle_system=None):
        """绘制像素风格的泡泡"""
        x, y = int(bubble.x), int(bubble.y)
        size = bubble.size
        
        # 获取泡泡颜色
        color = bubble.color
        
        # 主体：像素化的圆形（使用方块组成）
        radius = size // 2
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                dist = math.sqrt(dx*dx + dy*dy)
                if dist <= radius:
                    # 绘制像素点
                    px = x + dx
                    py = y + dy
                    if 0 <= px < screen.get_width() and 0 <= py < screen.get_height():
                        # 根据距离计算亮度
                        brightness = 1.0 - (dist / radius) * 0.3
                        adjusted_color = tuple(int(c * brightness) for c in color)
                        pygame.draw.circle(screen, adjusted_color, (px, py), 1)
        
        # 外轮廓和高光
        pygame.draw.circle(screen, (255, 255, 255), (x, y), size, 2)
        
        # 高光点
        hl_x = x - size // 4
        hl_y = y - size // 4
        pygame.draw.circle(screen, (255, 255, 255), (hl_x, hl_y), 4)
        
        # 特殊效果
        if bubble.type == 'ctrlc':
            # 闪电效果
            if pygame.time.get_ticks() % 400 < 200:
                for angle in range(0, 360, 90):
                    rad = math.radians(angle)
                    spark_x = int(x + math.cos(rad) * (size + 8))
                    spark_y = int(y + math.sin(rad) * (size + 8))
                    pygame.draw.circle(screen, (255, 255, 100), (spark_x, spark_y), 3)
        
        elif bubble.type == 'typeerror':
            # 旋转箭头效果
            if pygame.time.get_ticks() % 600 < 300:
                for angle in [45, 135, 225, 315]:
                    rad = math.radians(angle)
                    arrow_x = int(x + math.cos(rad) * (size + 10))
                    arrow_y = int(y + math.sin(rad) * (size + 10))
                    pygame.draw.circle(screen, (255, 100, 100), (arrow_x, arrow_y), 3)
        
        # 绘制泡泡标签
        label_map = {
            'pow': 'pow()',
            'delete': 'delete',
            'print': 'print',
            'ctrlc': 'Ctrl+C',
            'typeerror': 'TypeError'
        }
        
        if bubble.type in label_map:
            from settings import font_bubble, BLACK
            label = label_map[bubble.type]
            text = font_bubble.render(label, True, BLACK)
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)


class PixelKeyPlatformRenderer:
    """像素风格键盘平台渲染器"""
    
    def __init__(self):
        # 平台颜色定义
        self.platform_colors = {
            'primary': (210, 180, 255),     # 主颜色（浅紫）
            'light': (245, 235, 255),       # 亮面
            'side': (190, 160, 210),        # 侧面
            'shadow': (140, 110, 160),      # 阴影
            'highlight': (255, 250, 255),   # 高光
            'text': (80, 40, 110)           # 文字颜色
        }
        
        # 炫光效果
        self.glow_effect = PixelGlowEffect(
            self.platform_colors['primary'],
            glow_colors=[
                (200, 100, 255, 200),    # 外层：鲜紫
                (220, 150, 255, 100),    # 中层：浅紫
                (240, 200, 255, 50),     # 内层：很浅
            ],
            glow_size=12
        )
        
        # 粒子系统
        self.particle_system = PixelParticleSystem()
    
    def draw_platform(self, screen, platform):
        """绘制像素风格的平台"""
        if platform.is_broken:
            self._draw_broken_platform(screen, platform)
            return
        
        rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
        
        # 绘制炫光外围
        intensity = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.005)
        self.glow_effect.draw_glow(screen, rect, intensity)
        
        # 创建像素化平台外观
        PX = 4  # 像素大小
        sw = max(6, platform.width // PX)
        sh = max(4, platform.height // PX)
        
        small = pygame.Surface((sw, sh), pygame.SRCALPHA)
        small.fill((0, 0, 0, 0))
        
        # 投影
        pygame.draw.rect(small, self.platform_colors['shadow'], 
                        (1, 1, sw - 1, sh - 1))
        
        # 侧面（3D效果）
        side_h = max(1, sh // 4)
        pygame.draw.rect(small, self.platform_colors['side'], 
                        (0, sh - side_h, sw, side_h))
        
        # 顶面（主颜色）
        top_h = sh - side_h
        pygame.draw.rect(small, self.platform_colors['primary'], 
                        (0, 0, sw, top_h))
        
        # 顶部高光条（像素感）
        hl_h = max(1, top_h // 3)
        pygame.draw.rect(small, self.platform_colors['highlight'], 
                        (1, 1, sw - 2, hl_h))
        
        # 添加细节纹理（像素网格）
        for i in range(0, sw, 2):
            pygame.draw.line(small, self.platform_colors['highlight'],
                           (i, 0), (i, hl_h), 1)
        
        # 缩放回原始大小（保持像素感）
        try:
            scaled = pygame.transform.scale(small, (platform.width, platform.height))
            screen.blit(scaled, rect.topleft)
        except:
            pygame.draw.rect(screen, self.platform_colors['primary'], rect)
        
        # 边框轮廓
        edge_color = (max(0, self.platform_colors['side'][0] - 30),
                     max(0, self.platform_colors['side'][1] - 30),
                     max(0, self.platform_colors['side'][2] - 30))
        pygame.draw.rect(screen, edge_color, rect, 2)
        
        # 绘制标签
        from settings import font_key, BLACK
        label_text = font_key.render(platform.label, True, self.platform_colors['text'])
        label_rect = label_text.get_rect(center=rect.center)
        screen.blit(label_text, label_rect)
        
        # 动态平台指示
        if platform.is_dynamic:
            arrow = "↕"
            from settings import font_tiny
            arrow_text = font_tiny.render(arrow, True, self.platform_colors['primary'])
            arrow_rect = arrow_text.get_rect(
                center=(platform.x + platform.width // 2, platform.y - 12)
            )
            screen.blit(arrow_text, arrow_rect)
    
    def _draw_broken_platform(self, screen, platform):
        """绘制断裂的平台"""
        # 绘制冰块碎片
        for shard in platform.ice_shards:
            if shard['alpha'] <= 0:
                continue
            
            surf = pygame.Surface((int(shard['w']), int(shard['h'])), pygame.SRCALPHA)
            
            # 冰块主体
            color_with_alpha = (*shard['color'][:3], int(shard['alpha']))
            pygame.draw.rect(surf, color_with_alpha, 
                           (0, 0, int(shard['w']), int(shard['h'])))
            
            # 像素纹理
            for i in range(0, int(shard['w']), 3):
                pygame.draw.line(surf, (255, 255, 255, int(shard['alpha'] * 0.5)),
                               (i, 0), (i, int(shard['h'])), 1)
            
            # 边缘
            edge_color = (210, 185, 220, int(shard['alpha'] * 0.8))
            pygame.draw.rect(surf, edge_color, (0, 0, int(shard['w']), int(shard['h'])), 2)
            
            # 旋转并绘制
            rotated = pygame.transform.rotate(surf, shard['rotation'])
            rotated_rect = rotated.get_rect(
                center=(int(shard['x'] + shard['w'] / 2),
                       int(shard['y'] + shard['h'] / 2))
            )
            screen.blit(rotated, rotated_rect)
    
    def update(self):
        """更新粒子系统"""
        self.particle_system.update()
    
    def draw_particles(self, screen):
        """绘制粒子"""
        self.particle_system.draw(screen)
    
    def emit_platform_hit(self, x, y):
        """在平台被击中时发射粒子"""
        self.particle_system.emit_burst(
            x, y, 
            color=(200, 100, 255),
            count=6,
            speed_range=(0.5, 2),
            lifetime=20
        )