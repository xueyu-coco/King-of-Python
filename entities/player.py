import pygame
import random
from settings import *

class Player:
    def __init__(self, x, y, color, controls, facing_right=True):
        self.x = x
        self.y = y
        self.width = 40
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
        
    def update(self, keys, platforms):
        # 更新反转状态
        if self.is_reversed:
            self.reverse_timer -= 1
            if self.reverse_timer <= 0:
                self.is_reversed = False
                self.reverse_timer = 0
        
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
    
    def reverse_controls(self):
        """反转玩家控制"""
        self.is_reversed = True
        self.reverse_timer = REVERSED_DURATION
    
    def draw(self, screen):
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
            
            frozen_color = (
                min(255, self.color[0] + 100),
                min(255, self.color[1] + 150),
                255
            )
            pygame.draw.rect(screen, frozen_color, 
                           (int(self.x), int(self.y), self.width, self.height))
            pygame.draw.rect(screen, CYAN, 
                           (int(self.x), int(self.y), self.width, self.height), 2)
            
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
            
            pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))
            pygame.draw.rect(screen, BLACK, (int(self.x), int(self.y), self.width, self.height), 2)
        
        eye_y = int(self.y + 15)
        left_eye = (int(self.x + 12), eye_y)
        right_eye = (int(self.x + 28), eye_y)
        
        # 眼睛颜色根据状态变化
        if self.is_frozen:
            eye_color = CYAN
        elif self.is_reversed:
            eye_color = DARK_RED
        else:
            eye_color = BLACK
        pygame.draw.circle(screen, eye_color, left_eye, 4)
        pygame.draw.circle(screen, eye_color, right_eye, 4)
        
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