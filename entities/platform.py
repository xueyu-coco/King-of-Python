import pygame
from settings import *

class KeyPlatform:
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
        self.break_threshold = 1  # 立即断裂 = 1帧
        self.respawn_timer = 0  # 重生计时
        self.respawn_time = 180  # 3秒 = 180帧
        self.player_on_platform = False
        
    def update(self, players=None):
        """更新动态平台位置和断裂状态"""
        # 动态移动（即使可以断裂也能移动）
        if self.is_dynamic and not self.is_broken:
            self.y += self.move_speed * self.move_direction
            
            # 到达边界时反转方向
            if self.y <= self.base_y - self.move_range:
                self.move_direction = 1
            elif self.y >= self.base_y + self.move_range:
                self.move_direction = -1
        
        # 断裂机制
        if self.is_breakable:
            if self.is_broken:
                # 重生倒计时
                self.respawn_timer += 1
                if self.respawn_timer >= self.respawn_time:
                    self.is_broken = False
                    self.break_timer = 0
                    self.respawn_timer = 0
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
                            break
                
                # 如果没有玩家，重置计时
                if not self.player_on_platform:
                    self.break_timer = max(0, self.break_timer - 2)  # 慢慢恢复
                
                # 检查是否达到断裂条件
                if self.break_timer >= self.break_threshold:
                    self.is_broken = True
                    self.break_timer = 0
    
    def check_player_standing(self, player):
        """检查玩家是否站在平台上"""
        # 玩家底部在平台顶部附近
        return (player.x < self.x + self.width and
                player.x + player.width > self.x and
                player.y + player.height >= self.y and
                player.y + player.height <= self.y + 10 and
                player.on_ground)
    
    def draw(self, screen):
        """绘制3D键帽效果"""
        # 如果已断裂，绘制碎片效果
        if self.is_broken:
            self._draw_broken_pieces(screen)
            return
        
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
        # 优先判断是否动态+可断裂（Shift键）
        if self.is_dynamic and self.is_breakable:
            # Shift键：冰蓝色基础，根据破损程度变化
            damage_ratio = self.break_timer / self.break_threshold
            if damage_ratio > 0:
                # 从冰蓝色逐渐变红
                r = int(200 + damage_ratio * 55)
                g = int(220 - damage_ratio * 100)
                b = int(255 - damage_ratio * 55)  # 保持较高的蓝色值
                key_color = (r, g, b)
            else:
                # 完好状态：冰蓝色
                key_color = (200, 220, 255)
        elif self.is_dynamic:
            # 仅动态平台：浅蓝色
            key_color = (200, 220, 255)
        elif self.is_breakable:
            # 仅可断裂平台
            damage_ratio = self.break_timer / self.break_threshold
            if damage_ratio > 0:
                r = int(200 + damage_ratio * 55)
                g = int(220 - damage_ratio * 100)
                b = int(255 - damage_ratio * 155)
                key_color = (r, g, b)
            else:
                key_color = KEY_COLOR
        else:
            # 普通平台
            key_color = KEY_COLOR
            
        pygame.draw.rect(screen, key_color, 
                        (self.x, self.y, self.width, self.height))
        
        # 绘制裂痕效果
        if self.is_breakable and self.break_timer > 0:
            self._draw_cracks(screen)
        
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
            arrow = "↕"
            arrow_text = font_tiny.render(arrow, True, BLUE)
            arrow_rect = arrow_text.get_rect(
                center=(self.x + self.width//2, self.y - 15)
            )
            screen.blit(arrow_text, arrow_rect)
        
        # 可断裂平台警告
        if self.is_breakable and self.player_on_platform:
            # 显示破损进度条
            bar_width = self.width - 10
            bar_height = 4
            bar_x = self.x + 5
            bar_y = self.y + self.height + 5
            
            # 背景
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            # 进度
            progress_width = int(bar_width * (self.break_timer / self.break_threshold))
            progress_color = (255, int(255 * (1 - self.break_timer / self.break_threshold)), 0)
            pygame.draw.rect(screen, progress_color, (bar_x, bar_y, progress_width, bar_height))
            
            # 警告图标
            if self.break_timer > self.break_threshold * 0.5:
                warning_text = font_tiny.render("⚠", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(
                    center=(self.x + self.width//2, self.y - 25)
                )
                if pygame.time.get_ticks() % 500 < 250:  # 闪烁
                    screen.blit(warning_text, warning_rect)
    
    def _draw_cracks(self, screen):
        """绘制裂痕"""
        damage_ratio = self.break_timer / self.break_threshold
        crack_color = (80, 80, 80)
        
        # 根据损坏程度绘制不同数量的裂痕
        if damage_ratio > 0.2:
            # 第一道裂痕 - 左上到右下
            start_x = self.x + 10
            start_y = self.y + 5
            end_x = self.x + self.width - 10
            end_y = self.y + self.height - 5
            pygame.draw.line(screen, crack_color, (start_x, start_y), (end_x, end_y), 2)
        
        if damage_ratio > 0.4:
            # 第二道裂痕 - 右上到左下
            start_x = self.x + self.width - 10
            start_y = self.y + 5
            end_x = self.x + 10
            end_y = self.y + self.height - 5
            pygame.draw.line(screen, crack_color, (start_x, start_y), (end_x, end_y), 2)
        
        if damage_ratio > 0.6:
            # 第三道裂痕 - 横向
            mid_y = self.y + self.height // 2
            pygame.draw.line(screen, crack_color, 
                           (self.x + 5, mid_y), 
                           (self.x + self.width - 5, mid_y), 2)
        
        if damage_ratio > 0.8:
            # 第四道裂痕 - 纵向
            mid_x = self.x + self.width // 2
            pygame.draw.line(screen, crack_color, 
                           (mid_x, self.y + 5), 
                           (mid_x, self.y + self.height - 5), 2)
    
    def _draw_broken_pieces(self, screen):
        """绘制断裂后的碎片效果"""
        # 碎片逐渐消失的透明度
        alpha = max(0, 255 - int(255 * (self.respawn_timer / self.respawn_time)))
        
        if alpha > 0:
            # 创建半透明表面
            piece_surface = pygame.Surface((self.width, self.height))
            piece_surface.set_alpha(alpha)
            
            # 绘制几个分散的碎片（冰蓝色）
            piece_color = (180, 200, 235)  # 冰蓝色碎片
            piece_width = self.width // 3
            piece_height = self.height // 2
            
            # 左碎片（下落）
            offset_y = int(self.respawn_timer * 2)
            pygame.draw.rect(piece_surface, piece_color, 
                           (0, offset_y, piece_width, piece_height))
            
            # 中碎片（下落更快）
            offset_y2 = int(self.respawn_timer * 3)
            pygame.draw.rect(piece_surface, piece_color, 
                           (piece_width, offset_y2, piece_width, piece_height))
            
            # 右碎片（下落）
            offset_y3 = int(self.respawn_timer * 2.5)
            pygame.draw.rect(piece_surface, piece_color, 
                           (piece_width * 2, offset_y3, piece_width, piece_height))
            
            screen.blit(piece_surface, (self.x, self.y))
        
        # 显示重生倒计时
        if self.respawn_timer > 0:
            respawn_text = font_tiny.render("Respawning...", True, CYAN)
            text_rect = respawn_text.get_rect(
                center=(self.x + self.width//2, self.y + self.height//2)
            )
            screen.blit(respawn_text, text_rect)  