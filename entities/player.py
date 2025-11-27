import pygame
import random
import os
from settings import *

class Player:
    def __init__(self, x, y, color, controls, facing_right=True, avatar=None):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.hp = 100
        self.max_hp = 100
        self.on_ground = False
        self.facing_right = facing_right
        self.controls = controls
        
        self.skill = None
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_power = 3
        self.knockback_x = 0
        
        self.is_frozen = False
        self.freeze_timer = 0
        
        # 反转状态
        self.is_reversed = False
        self.reverse_timer = 0
        
        # super() 形态
        self.is_super = False
        self.super_timer = 0
        self.super_duration = 300  # 5秒 = 300帧（60fps）
        self.super_collision_cooldown = 0  # 碰撞冷却，防止连续伤害

        # 尝试加载玩家贴图（frame1.png 用于蓝色玩家，frame2.png 用于红色玩家）
        self.image1 = None
        self.image2 = None
        self._flipped_image1 = None
        self._flipped_image2 = None
        def _try_load(name):
            # 尝试多个常见路径
            candidates = [
                name,
                os.path.join(os.path.dirname(__file__), name),
                os.path.join(os.path.dirname(__file__), '..', name),
                os.path.join(os.path.dirname(__file__), '..', 'assets', name),
            ]
            for p in candidates:
                try:
                    surf = pygame.image.load(p).convert_alpha()
                    return surf
                except Exception:
                    continue
            return None

        # 只尝试在初始化一次加载资源并缩放到玩家尺寸
        raw1 = _try_load('frame1.png')
        raw2 = _try_load('frame2.png')
        if raw1:
            try:
                self.image1 = pygame.transform.smoothscale(raw1, (self.width, self.height))
            except Exception:
                self.image1 = pygame.transform.scale(raw1, (self.width, self.height))
        if raw2:
            try:
                self.image2 = pygame.transform.smoothscale(raw2, (self.width, self.height))
            except Exception:
                self.image2 = pygame.transform.scale(raw2, (self.width, self.height))

        # 根据传入的颜色选择默认显示帧（如果两帧都存在，蓝色用frame1，红色用frame2）
        self.use_image = False
        if (self.image1 or self.image2):
            self.use_image = True
            if color == BLUE and self.image1:
                self.current_image = self.image1
            elif color == RED and self.image2:
                self.current_image = self.image2
            else:
                # 如果颜色无法判断，优先使用image1然后image2
                self.current_image = self.image1 or self.image2
        else:
            self.current_image = None

        # 可选的头像（来自 face capture 或外部加载的 Surface）
        self.avatar = avatar
        self._cached_avatar = None
        
    def update(self, keys, platforms):
        # 更新反转状态
        if self.is_reversed:
            self.reverse_timer -= 1
            if self.reverse_timer <= 0:
                self.is_reversed = False
                self.reverse_timer = 0
        
        # 更新 super() 形态
        if self.is_super:
            self.super_timer -= 1
            if self.super_timer <= 0:
                self.is_super = False
                self.super_timer = 0
            # super() 形态下的碰撞冷却
            if self.super_collision_cooldown > 0:
                self.super_collision_cooldown -= 1
        
        # 更新冻结状态
        if self.is_frozen:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.is_frozen = False
                self.freeze_timer = 0
            self.vel_x = 0
            self.vel_y += GRAVITY
            self.y += self.vel_y
            
            self.on_ground = False
            for platform in platforms:
                if self.check_platform_collision(platform):
                    if self.vel_y > 0:
                        self.y = platform.y - self.height
                        self.vel_y = 0
                        self.on_ground = True
                        break
            
            return
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame > 15:
                self.is_attacking = False
                self.attack_frame = 0
        
        if abs(self.knockback_x) > 0.1:
            self.x += self.knockback_x
            self.knockback_x *= 0.8
        else:
            self.knockback_x = 0
        
        # 控制移动（考虑反转状态）
        left_pressed = keys[self.controls['left']]
        right_pressed = keys[self.controls['right']]
        
        # 如果反转，交换左右
        if self.is_reversed:
            left_pressed, right_pressed = right_pressed, left_pressed
        
        if left_pressed and not self.is_attacking:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        elif right_pressed and not self.is_attacking:
            self.vel_x = MOVE_SPEED
            self.facing_right = True
        else:
            self.vel_x = 0
        
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
        
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 检测所有平台
        self.on_ground = False
        for platform in platforms:
            if self.check_platform_collision(platform):
                if self.vel_y > 0:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    break
        
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
        
        if self.y > HEIGHT:
            self.hp = 0
    
    def check_platform_collision(self, platform):
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y and
                self.vel_y >= 0)
    
    def use_skill(self):
        if self.skill and self.attack_cooldown <= 0:
            used_skill = self.skill
            self.skill = None
            self.attack_cooldown = ATTACK_COOLDOWN
            
            if used_skill in ['pow', 'delete']:
                self.is_attacking = True
                self.attack_frame = 0
            
            return used_skill
        return None
    
    def get_attack_rect(self):
        if not self.is_attacking:
            return None
        
        attack_width = 80
        attack_height = 60
        if self.facing_right:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - attack_width
        attack_y = self.y
        
        return {
            'x': attack_x,
            'y': attack_y,
            'width': attack_width,
            'height': attack_height
        }
    
    def take_damage(self, damage, knockback_direction):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        self.knockback_x = knockback_direction * 15
    
    def freeze(self):
        self.is_frozen = True
        self.freeze_timer = FREEZE_DURATION
        self.vel_x = 0
        # 播放冰冻音效（容错处理）
        try:
            # 初始化 mixer（如果尚未初始化）
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
            except Exception:
                pass
            # 构造 assets 路径并尝试加载播放短音效
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            ice_path = os.path.join(repo_root, 'assets', 'eufrosyyn_sfx_break_ice_a.mp3')
            try:
                ice_sound = pygame.mixer.Sound(ice_path)
                try:
                    ice_sound.set_volume(0.8)
                except Exception:
                    pass
                ice_sound.play()
            except Exception:
                # 如果加载或播放失败，不要抛出异常影响游戏
                pass
        except Exception:
            pass
    
    def reverse_controls(self):
        """反转玩家控制"""
        self.is_reversed = True
        self.reverse_timer = REVERSED_DURATION
    
    def activate_super(self):
        """激活 super() 形态"""
        self.is_super = True
        self.super_timer = self.super_duration
        self.skill = None  # 清除其他技能
    
    def check_super_collision(self, other_player):
        """检查 super() 形态下是否与对方碰撞"""
        if not self.is_super or self.super_collision_cooldown > 0:
            return False
        
        # 计算膨胀后的碰撞范围
        scale = 2.0
        expanded_width = self.width * scale
        expanded_height = self.height * scale
        expanded_x = self.x - (expanded_width - self.width) / 2
        expanded_y = self.y - (expanded_height - self.height) / 2
        
        # 检查是否与对方碰撞
        if (expanded_x < other_player.x + other_player.width and
            expanded_x + expanded_width > other_player.x and
            expanded_y < other_player.y + other_player.height and
            expanded_y + expanded_height > other_player.y):
            return True
        
        return False
    
    def draw(self, screen):
        # super() 形态绘制
        if self.is_super:
            import math
            
            # 绘制紫色光芒外环（多层光晕）
            glow_radius = int(self.width * 1.2)
            for i in range(3):
                alpha = int(100 * (1 - i / 3))
                glow_surf = pygame.Surface((glow_radius * 2 + i * 8, glow_radius * 2 + i * 8), pygame.SRCALPHA)
                glow_color = (200, 100, 255, alpha)
                pygame.draw.circle(glow_surf, glow_color, 
                                 (glow_radius + i * 4, glow_radius + i * 4), 
                                 glow_radius + i * 4)
                glow_rect = glow_surf.get_rect(center=(int(self.x + self.width // 2), 
                                                       int(self.y + self.height // 2)))
                screen.blit(glow_surf, glow_rect)
            
            # 绘制膨胀的玩家（2倍大小）
            scale = 2.0
            # 最后1秒闪烁效果
            if self.super_timer < 60 and (self.super_timer // 10) % 2 == 0:
                scale = 1.8
            
            expanded_width = int(self.width * scale)
            expanded_height = int(self.height * scale)
            expand_offset_x = (expanded_width - self.width) / 2
            expand_offset_y = (expanded_height - self.height) / 2
            
            super_rect = pygame.Rect(
                int(self.x - expand_offset_x),
                int(self.y - expand_offset_y),
                expanded_width,
                expanded_height
            )
            
            # 绘制膨胀的头像或方块
            if self.use_image and self.current_image:
                try:
                    expanded_img = pygame.transform.smoothscale(self.current_image, 
                                                               (expanded_width, expanded_height))
                    if not self.facing_right:
                        expanded_img = pygame.transform.flip(expanded_img, True, False)
                    screen.blit(expanded_img, super_rect.topleft)
                except:
                    super_color = (min(255, self.color[0] + 50),
                                 min(255, self.color[1] + 50),
                                 min(255, self.color[2] + 50))
                    pygame.draw.rect(screen, super_color, super_rect)
            else:
                super_color = (min(255, self.color[0] + 50),
                             min(255, self.color[1] + 50),
                             min(255, self.color[2] + 50))
                pygame.draw.rect(screen, super_color, super_rect)
            
            # 绘制紫色边框
            pygame.draw.rect(screen, (200, 100, 255), super_rect, 3)
            
            # 绘制倒计时
            super_seconds = self.super_timer // 60 + 1
            super_text = font_tiny.render(f"SUPER: {super_seconds}s", True, (200, 100, 255))
            text_rect = super_text.get_rect(center=(int(self.x + self.width // 2), 
                                                    int(self.y - 40)))
            screen.blit(super_text, text_rect)
            
            # 绘制旋转星星装饰
            star_count = 8
            for i in range(star_count):
                angle = (360 / star_count) * i + (pygame.time.get_ticks() % 360) * 2
                rad = math.radians(angle)
                star_dist = int(self.width * 0.7)
                star_x = int(self.x + self.width // 2 + math.cos(rad) * star_dist)
                star_y = int(self.y + self.height // 2 + math.sin(rad) * star_dist)
                pygame.draw.circle(screen, (255, 215, 0), (star_x, star_y), 3)
            
            return  # super() 形态下提前返回，不绘制其他效果
        
        # 反转状态效果（红色边框闪烁）
        if self.is_reversed:
            # 绘制反转指示边框
            reverse_padding = 6
            if pygame.time.get_ticks() % 600 < 300:  # 闪烁效果
                pygame.draw.rect(screen, DARK_RED, 
                               (int(self.x - reverse_padding), int(self.y - reverse_padding), 
                                self.width + reverse_padding*2, self.height + reverse_padding*2), 4)
            
            # 显示反转倒计时
            reverse_seconds = self.reverse_timer // FPS + 1
            reverse_text = font_tiny.render(f"REVERSED: {reverse_seconds}s", True, DARK_RED)
            text_rect = reverse_text.get_rect(center=(int(self.x + self.width//2), 
                                                     int(self.y - 30)))
            screen.blit(reverse_text, text_rect)
            
            # 绘制反向箭头
            arrow_text = font_small.render("⇄", True, DARK_RED)
            arrow_rect = arrow_text.get_rect(center=(int(self.x + self.width//2), 
                                                     int(self.y - 50)))
            screen.blit(arrow_text, arrow_rect)
        
        # 冻结效果
        if self.is_frozen:
            ice_padding = 5
            pygame.draw.rect(screen, ICE_BLUE, 
                           (int(self.x - ice_padding), int(self.y - ice_padding), 
                            self.width + ice_padding*2, self.height + ice_padding*2), 3)
            # 如果加载了图片，则绘制图片并加上冻结边框和雪花
            if self.use_image and self.current_image:
                img = self.current_image
                if not self.facing_right:
                    if self._flipped_image1 is None and self.image1:
                        self._flipped_image1 = pygame.transform.flip(self.image1, True, False)
                    if self._flipped_image2 is None and self.image2:
                        self._flipped_image2 = pygame.transform.flip(self.image2, True, False)
                    # 选择对应翻转图
                    if self.current_image == self.image1 and self._flipped_image1:
                        img = self._flipped_image1
                    elif self.current_image == self.image2 and self._flipped_image2:
                        img = self._flipped_image2
                    else:
                        img = pygame.transform.flip(self.current_image, True, False)
                screen.blit(img, (int(self.x), int(self.y)))
                # 如果有头像，将头像居中绘制在frame中间
                if self.avatar:
                    aw, ah = self.avatar.get_size()
                    max_w = int(self.width * 0.5)
                    max_h = int(self.height * 0.5)
                    scale = min(max_w / aw if aw else 1, max_h / ah if ah else 1, 1)
                    new_w = max(1, int(aw * scale))
                    new_h = max(1, int(ah * scale))
                    try:
                        avatar_surf = pygame.transform.smoothscale(self.avatar, (new_w, new_h))
                    except Exception:
                        avatar_surf = pygame.transform.scale(self.avatar, (new_w, new_h))
                    ax = int(self.x + (self.width - avatar_surf.get_width()) / 2)
                    ay = int(self.y + (self.height - avatar_surf.get_height()) / 2)
                    screen.blit(avatar_surf, (ax, ay))
            else:
                frozen_color = (
                    min(255, self.color[0] + 100),
                    min(255, self.color[1] + 150),
                    255
                )
                pygame.draw.rect(screen, frozen_color, (int(self.x), int(self.y), self.width, self.height))
                pygame.draw.rect(screen, CYAN, (int(self.x), int(self.y), self.width, self.height), 2)
            
            for i in range(3):
                snowflake_x = int(self.x + self.width//2 + random.randint(-15, 15))
                snowflake_y = int(self.y + random.randint(0, self.height))
                pygame.draw.circle(screen, WHITE, (snowflake_x, snowflake_y), 2)
            
            freeze_seconds = self.freeze_timer // FPS + 1
            freeze_text = font_tiny.render(f"FROZEN: {freeze_seconds}s", True, CYAN)
            text_rect = freeze_text.get_rect(center=(int(self.x + self.width//2), 
                                                     int(self.y - 20)))
            screen.blit(freeze_text, text_rect)
        else:
            if self.is_attacking and self.attack_frame % 4 < 2:
                color = (min(255, self.color[0] + 50), 
                        min(255, self.color[1] + 50), 
                        min(255, self.color[2] + 50))
            else:
                color = self.color
            # 绘制玩家：优先使用图片，否则回退到方块
            if self.use_image and self.current_image:
                img = self.current_image
                # 根据朝向选择是否翻转
                if not self.facing_right:
                    # 预缓存翻转图以提高性能
                    if self.current_image == self.image1:
                        if self._flipped_image1 is None and self.image1:
                            self._flipped_image1 = pygame.transform.flip(self.image1, True, False)
                        img = self._flipped_image1 or pygame.transform.flip(self.image1, True, False)
                    elif self.current_image == self.image2:
                        if self._flipped_image2 is None and self.image2:
                            self._flipped_image2 = pygame.transform.flip(self.image2, True, False)
                        img = self._flipped_image2 or pygame.transform.flip(self.image2, True, False)
                    else:
                        img = pygame.transform.flip(self.current_image, True, False)
                screen.blit(img, (int(self.x), int(self.y)))
                if self.avatar:
                    aw, ah = self.avatar.get_size()
                    max_w = int(self.width * 0.5)
                    max_h = int(self.height * 0.5)
                    scale = min(max_w / aw if aw else 1, max_h / ah if ah else 1, 1)
                    new_w = max(1, int(aw * scale))
                    new_h = max(1, int(ah * scale))
                    try:
                        avatar_surf = pygame.transform.smoothscale(self.avatar, (new_w, new_h))
                    except Exception:
                        avatar_surf = pygame.transform.scale(self.avatar, (new_w, new_h))
                    ax = int(self.x + (self.width - avatar_surf.get_width()) / 2)
                    ay = int(self.y + (self.height - avatar_surf.get_height()) / 2)
                    screen.blit(avatar_surf, (ax, ay))
            else:
                pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))
                if self.avatar:
                    aw, ah = self.avatar.get_size()
                    max_w = int(self.width * 0.5)
                    max_h = int(self.height * 0.5)
                    scale = min(max_w / aw if aw else 1, max_h / ah if ah else 1, 1)
                    new_w = max(1, int(aw * scale))
                    new_h = max(1, int(ah * scale))
                    try:
                        avatar_surf = pygame.transform.smoothscale(self.avatar, (new_w, new_h))
                    except Exception:
                        avatar_surf = pygame.transform.scale(self.avatar, (new_w, new_h))
                    ax = int(self.x + (self.width - avatar_surf.get_width()) / 2)
                    ay = int(self.y + (self.height - avatar_surf.get_height()) / 2)
                    screen.blit(avatar_surf, (ax, ay))
        
        # 已移除眼睛绘制（使用图片或方块作为视觉表现）
        
        if self.skill and not self.is_frozen:
            indicator_x = int(self.x + self.width // 2)
            indicator_y = int(self.y - 15)
            
            if self.skill == 'pow':
                skill_color = ORANGE
                skill_text = 'pow()'
            elif self.skill == 'delete':
                skill_color = RED
                skill_text = 'del'
            elif self.skill == 'print':
                skill_color = YELLOW
                skill_text = 'prn'
            else:
                skill_color = WHITE
                skill_text = '?'
            
            pygame.draw.circle(screen, skill_color, (indicator_x, indicator_y), 8)
            tiny_text = pygame.font.Font(None, 14).render(skill_text, True, BLACK)
            text_rect = tiny_text.get_rect(center=(indicator_x, indicator_y))
            screen.blit(tiny_text, text_rect)
        
        attack_rect = self.get_attack_rect()
        if attack_rect and not self.is_frozen:
            pygame.draw.rect(screen, (255, 200, 0, 128), 
                           (attack_rect['x'], attack_rect['y'], 
                            attack_rect['width'], attack_rect['height']), 3)  