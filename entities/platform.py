import pygame
import random
import math
from settings import *

# Purple palette for platforms (local variants for contrast)
# Use global PURPLE from settings and derive lighter/darker tones.
# Adopt a softer, brighter pastel purple palette (lighter and less saturated)
P_PRIMARY = (210, 180, 255)    # main pastel purple
P_LIGHT = (245, 235, 255)      # very light top face (bright, pastel)
P_SIDE = (190, 160, 210)       # soft side tone for subtle 3D
P_SHADOW = (140, 110, 160)     # muted shadow (not too dark)
P_HIGHLIGHT = (255, 250, 255)  # near-white highlight for sparkle
P_TEXT = (80, 40, 110)         # readable but softer dark purple for labels

class KeyPlatform:
    def _draw_bottom_glow(self, screen, rect):
        """在键帽底部绘制一条发光的像素条，增强立体感"""
        # 发光颜色使用外描边同色系
        base = (193, 104, 255)
        # 计算发光区域尺寸（像素风的薄条，向下衰减）
        pad = max(2, self.width // 20)  # 左右扩展少量像素
        glow_h = max(4, self.height // 10)
        glow_w = rect.width + pad * 2
        surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)

        # 顶部最亮的1px亮条
        pygame.draw.rect(surf, (*base, 230), (2, 0, glow_w - 4, 1))

        # 向下逐行降低透明度，形成像素化的发光渐变
        alphas = [160, 110, 70, 40, 20]
        for i, a in enumerate(alphas, start=1):
            if i >= glow_h:
                break
            # 稍微左右收缩，保留像素层次感
            inset = max(0, 2 - i)
            pygame.draw.rect(surf, (*base, a), (inset, i, glow_w - inset * 2, 1))

        # 将发光条放在键帽底部外侧
        screen.blit(surf, (rect.x - pad, rect.bottom))

    def _glow_factor(self):
        """返回发光强度系数。动态平台进行轻微呼吸动画。"""
        if getattr(self, "is_dynamic", False):
            t = pygame.time.get_ticks() * 0.006
            # 0.85 ~ 1.15 的平滑波动
            return 0.85 + 0.30 * (0.5 * (math.sin(t) + 1.0))
        return 1.0

    def _draw_edge_glow(self, screen, rect, side):
        """在指定边绘制像素风发光条: side in ['bottom','top','left','right']。
        包含第一层亮条和第二层更淡的外扩光晕。"""
        base = (193, 104, 255)
        factor = self._glow_factor()
        # 加粗外发光：增加层数与逐步衰减的 alpha 值
        base_alphas = [200, 160, 120, 85, 55, 35, 20, 10]  # 主层更多行形成更厚的主体辉光
        alphas = [min(255, max(0, int(a * factor))) for a in base_alphas]
        second_base = [90, 65, 45, 30, 18, 10]  # 第二层外扩柔光
        second_alphas = [min(255, max(0, int(a * factor * 0.85))) for a in second_base]

        if side in ("bottom", "top"):
            # 顶部/底部加粗：增加高度
            glow_h = max(6, self.height // 8)
            glow_w = rect.width
            surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)

            if side == "bottom":
                # 靠近键帽边缘处最亮
                pygame.draw.rect(surf, (*base, min(255, int(230 * factor))), (2, 0, glow_w - 4, 1))
                for i, a in enumerate(alphas, start=1):
                    if i >= glow_h:
                        break
                    inset = max(0, 2 - i)
                    pygame.draw.rect(surf, (*base, a), (inset, i, glow_w - inset * 2, 1))
                screen.blit(surf, (rect.x, rect.bottom))
                # 第二层更淡的外扩光
                ext_h = max(3, glow_h // 2)
                surf2 = pygame.Surface((glow_w, ext_h), pygame.SRCALPHA)
                for j, a2 in enumerate(second_alphas):
                    if j >= ext_h:
                        break
                    inset2 = max(0, 2 - j)
                    pygame.draw.rect(surf2, (*base, a2), (inset2, j, glow_w - inset2 * 2, 1))
                screen.blit(surf2, (rect.x, rect.bottom + glow_h))
            else:  # top
                # 亮边靠近键帽底部（surf 底部）
                pygame.draw.rect(surf, (*base, min(255, int(230 * factor))), (2, glow_h - 1, glow_w - 4, 1))
                for i, a in enumerate(alphas, start=1):
                    if i >= glow_h:
                        break
                    inset = max(0, 2 - i)
                    y = glow_h - 1 - i
                    pygame.draw.rect(surf, (*base, a), (inset, y, glow_w - inset * 2, 1))
                screen.blit(surf, (rect.x, rect.top - glow_h))
                # 第二层更淡外扩光（向上）
                ext_h = max(3, glow_h // 2)
                surf2 = pygame.Surface((glow_w, ext_h), pygame.SRCALPHA)
                for j, a2 in enumerate(second_alphas):
                    if j >= ext_h:
                        break
                    inset2 = max(0, 2 - j)
                    y2 = ext_h - 1 - j
                    pygame.draw.rect(surf2, (*base, a2), (inset2, y2, glow_w - inset2 * 2, 1))
                screen.blit(surf2, (rect.x, rect.top - glow_h - ext_h))
        elif side in ("left", "right"):
            # 左右加粗：移除上下额外 pad，直接与键帽上下齐平，高度为键帽高度
            glow_w = max(6, self.width // 8)
            glow_h = rect.height
            surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)

            if side == "right":
                pygame.draw.rect(surf, (*base, min(255, int(230 * factor))), (0, 2, 1, glow_h - 4))
                for i, a in enumerate(alphas, start=1):
                    if i >= glow_w:
                        break
                    inset = max(0, 2 - i)
                    x = i
                    pygame.draw.rect(surf, (*base, a), (x, inset, 1, glow_h - inset * 2))
                screen.blit(surf, (rect.right, rect.top))
                # 第二层柔光外扩
                ext_w = max(3, glow_w // 2)
                surf2 = pygame.Surface((ext_w, glow_h), pygame.SRCALPHA)
                for j, a2 in enumerate(second_alphas):
                    if j >= ext_w:
                        break
                    inset2 = max(0, 2 - j)
                    x2 = j
                    pygame.draw.rect(surf2, (*base, a2), (x2, inset2, 1, glow_h - inset2 * 2))
                screen.blit(surf2, (rect.right + glow_w, rect.top))
            else:  # left
                pygame.draw.rect(surf, (*base, min(255, int(230 * factor))), (glow_w - 1, 2, 1, glow_h - 4))
                for i, a in enumerate(alphas, start=1):
                    if i >= glow_w:
                        break
                    inset = max(0, 2 - i)
                    x = glow_w - 1 - i
                    pygame.draw.rect(surf, (*base, a), (x, inset, 1, glow_h - inset * 2))
                screen.blit(surf, (rect.left - glow_w, rect.top))
                ext_w = max(3, glow_w // 2)
                surf2 = pygame.Surface((ext_w, glow_h), pygame.SRCALPHA)
                for j, a2 in enumerate(second_alphas):
                    if j >= ext_w:
                        break
                    inset2 = max(0, 2 - j)
                    x2 = ext_w - 1 - j
                    pygame.draw.rect(surf2, (*base, a2), (x2, inset2, 1, glow_h - inset2 * 2))
                screen.blit(surf2, (rect.left - glow_w - ext_w, rect.top))

    def _draw_glow_edges(self, screen, rect):
        """在四周绘制发光像素条"""
        # 加粗后的四周发光（上下 + 左右）
        self._draw_edge_glow(screen, rect, "bottom")
        self._draw_edge_glow(screen, rect, "top")
        self._draw_edge_glow(screen, rect, "left")
        self._draw_edge_glow(screen, rect, "right")

    def _draw_ice_texture(self, screen):
        ice_white = P_HIGHLIGHT
        # 随机但固定的冰晶线条（基于平台位置生成）
        random.seed(int(self.x + self.y))
        for i in range(5):
            x1 = self.x + random.randint(5, self.width - 5)
            y1 = self.y + random.randint(5, self.height - 5)
            x2 = x1 + random.randint(-20, 20)
            y2 = y1 + random.randint(-10, 10)
            # 限制在平台范围内
            x2 = max(self.x + 5, min(self.x + self.width - 5, x2))
            y2 = max(self.y + 5, min(self.y + self.height - 5, y2))
            pygame.draw.line(screen, ice_white, (x1, y1), (x2, y2), 1)
        # 绘制闪烁的冰晶点
        if pygame.time.get_ticks() % 1000 < 500:
            for i in range(3):
                px = self.x + random.randint(10, self.width - 10)
                py = self.y + random.randint(5, self.height - 5)
                pygame.draw.circle(screen, ice_white, (px, py), 2)
        random.seed()  # 恢复随机种子
    """键盘按键平台类"""
    def __init__(self, x, y, width, height, label, is_dynamic=False, is_breakable=False):
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
        
        # 可断裂平台相关
        self.is_breakable = is_breakable
        self.is_broken = False
        self.break_timer = 0  # 站在上面的计时
        self.break_threshold = 0  # 立即断裂 = 0帧（检测到就断）
        self.respawn_timer = 0  # 重生计时
        self.respawn_time = 180  # 3秒 = 180帧
        self.player_on_platform = False
        
        # 冰块碎片系统
        self.ice_shards = []
        
    def update(self, players=None):
        """更新动态平台位置和断裂状态"""
        # 动态移动（即使可以断裂也能移动）
        if self.is_dynamic and not self.is_broken:
            # 检查是否有 base_x 属性（水平移动）
            if hasattr(self, 'base_x'):
                # 检查是否有玩家站在平台上
                has_player = False
                if players:
                    for player in players:
                        if self.check_player_standing(player):
                            has_player = True
                            break
                
                # 根据是否有玩家调整速度
                current_speed = self.move_speed * 2.5 if has_player else self.move_speed
                
                # 水平移动
                self.x += current_speed * self.move_direction
                
                # 到达边界时反转方向
                if self.x <= self.base_x - self.move_range:
                    self.move_direction = 1
                elif self.x >= self.base_x + self.move_range:
                    self.move_direction = -1
            else:
                # 垂直移动
                self.y += self.move_speed * self.move_direction
                
                # 到达边界时反转方向
                if self.y <= self.base_y - self.move_range:
                    self.move_direction = 1
                elif self.y >= self.base_y + self.move_range:
                    self.move_direction = -1
        
        # 断裂机制
        if self.is_breakable:
            if self.is_broken:
                # 更新冰块碎片
                for shard in self.ice_shards[:]:
                    shard['x'] += shard['vx']
                    shard['y'] += shard['vy']
                    shard['vy'] += 0.5  # 重力
                    shard['rotation'] += shard['rot_speed']
                    shard['alpha'] -= 3  # 淡出
                    
                    # 移除完全透明或掉出屏幕的碎片
                    if shard['alpha'] <= 0 or shard['y'] > HEIGHT + 50:
                        self.ice_shards.remove(shard)
                
                # 重生倒计时
                self.respawn_timer += 1
                if self.respawn_timer >= self.respawn_time:
                    self.is_broken = False
                    self.break_timer = 0
                    self.respawn_timer = 0
                    self.ice_shards.clear()
                    # 重生时恢复到基准位置
                    self.y = self.base_y
            else:
                # 检测是否有玩家站在上面
                self.player_on_platform = False
                if players:
                    for player in players:
                        if self.check_player_standing(player):
                            self.player_on_platform = True
                            self.break_timer += 1
                            # 立即断裂
                            if self.break_timer > self.break_threshold:
                                self.is_broken = True
                                self.break_timer = 0
                                self._create_ice_shards()
                            break
                
                # 如果没有玩家，重置计时
                if not self.player_on_platform:
                    self.break_timer = 0
    
    def _create_ice_shards(self):
        """创建冰块碎片"""
        self.ice_shards.clear()
        
        # 创建多个不规则冰块碎片
        num_shards = 12
        for i in range(num_shards):
            # 随机大小和位置
            shard_w = random.randint(int(self.width * 0.15), int(self.width * 0.3))
            shard_h = random.randint(int(self.height * 0.4), int(self.height * 0.8))
            
            # 起始位置在平台范围内
            start_x = self.x + random.uniform(0, self.width - shard_w)
            start_y = self.y + random.uniform(0, self.height - shard_h)
            
            # 随机速度（向外爆炸效果）
            center_x = self.x + self.width / 2
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            
            shard = {
                'x': start_x,
                'y': start_y,
                'w': shard_w,
                'h': shard_h,
                'vx': math.cos(angle) * speed,
                'vy': -random.uniform(3, 8),  # 向上弹起
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-15, 15),
                'alpha': 255,
                'color': random.choice([
                    (240, 220, 255),  # very light purple
                    (230, 200, 255),  # light lavender
                    (210, 180, 255),  # pastel purple
                    (250, 235, 255),  # ultra pale
                ])
            }
            self.ice_shards.append(shard)
    
    def check_player_standing(self, player):
        """检查玩家是否站在平台上"""
        return (player.x < self.x + self.width and
                player.x + player.width > self.x and
                player.y + player.height >= self.y and
                player.y + player.height <= self.y + 10)
    
    def draw(self, screen):
        # 选择主面颜色
        if self.is_dynamic and self.is_breakable:
            key_color = P_LIGHT
        elif self.is_dynamic:
            key_color = P_LIGHT
        elif self.is_breakable:
            key_color = P_PRIMARY
        else:
            key_color = P_PRIMARY
        """绘制3D键帽效果"""
        # 如果已断裂，绘制冰块碎片
        if self.is_broken:
            self._draw_ice_shards(screen)
            # 不显示重生倒计时文字，但平台仍会在3秒后重生
            return
        

        # 将所有键帽改回像素风长方形（颜色保持不变）
        rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # 小画布像素化参数
        PX = 4
        sw = max(6, self.width // PX)
        sh = max(4, self.height // PX)

        small = pygame.Surface((sw, sh), pygame.SRCALPHA)
        small.fill((0, 0, 0, 0))

        # 投影（右下偏移）
        try:
            pygame.draw.rect(small, P_SHADOW, (1, 1, sw - 1, sh - 1))
        except Exception:
            pass

        # 侧面（底部像素条）
        side_h = max(1, sh // 4)
        pygame.draw.rect(small, P_SIDE, (0, sh - side_h, sw, side_h))

        # 顶面
        top_h = sh - side_h
        pygame.draw.rect(small, key_color, (0, 0, sw, top_h))

        # 顶部高光（像素条）
        hl_h = max(1, top_h // 4)
        pygame.draw.rect(small, P_HIGHLIGHT, (1, 1, sw - 2, hl_h))

        # 像素风斜角处理：原先透明，现在改为以白色填充形成“白色倒角”效果
        if sw > 6 and sh > 6:
            corner_clear = [(0,0),(1,0),(0,1), (sw-1,0),(sw-2,0),(sw-1,1), (0,sh-1),(0,sh-2),(1,sh-1), (sw-1,sh-1),(sw-2,sh-1),(sw-1,sh-2)]
            for (cx, cy) in corner_clear:
                # 仅清除顶面与阴影区域，不影响侧面底部条（避免破坏立体感）
                if cy < top_h:  # 顶面或高光区域
                    small.set_at((cx, cy), (255,255,255,255))

        # 缩放到目标尺寸（最近邻放大以保持像素感）
        try:
            scaled = pygame.transform.scale(small, (self.width, self.height))
            screen.blit(scaled, rect.topleft)
        except Exception:
            pygame.draw.rect(screen, key_color, rect)

        # 像素风外描边：使用独立 surface 并裁剪角落像素
        outline_color = (193, 104, 255)
        is_space = str(self.label).strip().lower() in ("space", "spacebar", "空格")
        if is_space:
            outline_rect = rect.copy()
        else:
            outline_rect = rect.inflate(2, 2)
        outline_surf = pygame.Surface((outline_rect.width, outline_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(outline_surf, outline_color, outline_surf.get_rect(), 2)
        # 描边角从透明改为白色填充（与顶面白角统一）
        ow, oh = outline_surf.get_width(), outline_surf.get_height()
        if ow > 6 and oh > 6:
            corner_blocks = [
                (0,0),(1,0),(0,1),
                (ow-1,0),(ow-2,0),(ow-1,1),
                (0,oh-1),(0,oh-2),(1,oh-1),
                (ow-1,oh-1),(ow-2,oh-1),(ow-1,oh-2)
            ]
            for (cx, cy) in corner_blocks:
                outline_surf.set_at((cx, cy), (255,255,255,255))
        screen.blit(outline_surf, outline_rect.topleft)

        # 细边框（1px）以突出键帽轮廓
        pygame.draw.rect(screen, (max(0, P_SIDE[0]-20), max(0, P_SIDE[1]-20), max(0, P_SIDE[2]-20)), rect, 1)

        # 四周发光像素条（增强立体感）
        self._draw_glow_edges(screen, rect)

        # 如果需要，绘制冰晶纹理（仍然使用单独方法）
        if (self.is_dynamic and self.is_breakable) or self.is_breakable:
            self._draw_ice_texture(screen)

        # 标签（居中）
        label_text = font_key.render(self.label, True, P_TEXT)
        label_rect = label_text.get_rect(center=rect.center)
        screen.blit(label_text, label_rect)

        # 动态平台额外标识（小箭头）
        if self.is_dynamic:
            arrow = "↕"
            arrow_text = font_tiny.render(arrow, True, P_PRIMARY)
            arrow_rect = arrow_text.get_rect(center=(self.x + self.width//2, self.y - 12))
            screen.blit(arrow_text, arrow_rect)
    
    def _draw_ice_shards(self, screen):
        """绘制飞散的冰块碎片"""
        for shard in self.ice_shards:
            if shard['alpha'] <= 0:
                continue
            
            # 创建带旋转的冰块碎片
            surf = pygame.Surface((int(shard['w']), int(shard['h'])), pygame.SRCALPHA)
            
            # 绘制冰块主体
            color_with_alpha = (*shard['color'][:3], int(shard['alpha']))
            pygame.draw.rect(surf, color_with_alpha, (0, 0, int(shard['w']), int(shard['h'])))
            
            # 添加高光（更浅的紫色高光）
            highlight_color = (255, 250, 255, int(shard['alpha'] * 0.6))
            pygame.draw.rect(surf, highlight_color, (2, 2, max(1, int(shard['w']) - 4), max(1, int(shard['h'] * 0.3))), 1)
            
            # 添加边缘裂纹（浅紫色边缘）
            edge_color = (210, 185, 220, int(shard['alpha'] * 0.8))
            pygame.draw.rect(surf, edge_color, (0, 0, int(shard['w']), int(shard['h'])), 2)
            
            # 旋转碎片
            rotated = pygame.transform.rotate(surf, shard['rotation'])
            rotated_rect = rotated.get_rect(center=(int(shard['x'] + shard['w']/2), 
                                                     int(shard['y'] + shard['h']/2)))
            
            screen.blit(rotated, rotated_rect)
            
            # 绘制飞散的冰晶粒子
            if random.random() < 0.3:
                particle_x = int(shard['x'] + shard['w']/2 + random.randint(-5, 5))
                particle_y = int(shard['y'] + shard['h']/2 + random.randint(-5, 5))
                particle_color = (240, 210, 255, int(shard['alpha'] * 0.5))
                pygame.draw.circle(screen, particle_color, (particle_x, particle_y), 1)  