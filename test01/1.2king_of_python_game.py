import pygame
import random
import math

# 初始化Pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King of Python - 双人对抗")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 220, 0)
GREEN = (80, 200, 80)
ORANGE = (255, 165, 0)
PURPLE = (180, 80, 255)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (205, 133, 63)
GOLD = (255, 215, 0)

# 游戏设置
FPS = 60
MOVE_SPEED = 8
BUBBLE_SPAWN_TIME = 90

# 字体
font_large = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 56)
font_small = pygame.font.Font(None, 36)

class Player:
    def __init__(self, x, y, color, name, controls):
        self.x = x
        self.y = y
        self.width = 70
        self.height = 100
        self.color = color
        self.name = name
        self.vel_x = 0
        self.hp = 100
        self.max_hp = 100
        self.energy = 100
        self.max_energy = 100
        self.facing_right = True
        self.controls = controls
        self.stunned = False
        self.stun_timer = 0
        self.hit_cooldown = 0
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_frame = 0
        
    def update(self, keys):
        # 处理眩晕状态
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # 处理攻击动画
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame > 15:
                self.is_attacking = False
                self.attack_frame = 0
        
        # 控制移动（除非被眩晕）
        if not self.stunned and not self.is_attacking:
            if keys[self.controls['left']]:
                self.vel_x = -MOVE_SPEED
                self.facing_right = False
            elif keys[self.controls['right']]:
                self.vel_x = MOVE_SPEED
                self.facing_right = True
            else:
                self.vel_x = 0
            
            # 攻击
            if keys[self.controls['attack']] and self.attack_cooldown <= 0:
                self.is_attacking = True
                self.attack_cooldown = 30
                self.energy = max(0, self.energy - 10)
        else:
            self.vel_x *= 0.9
        
        # 更新位置
        self.x += self.vel_x
        
        # 边界限制
        if self.x < 50:
            self.x = 50
        if self.x > WIDTH - 50 - self.width:
            self.x = WIDTH - 50 - self.width
        
        # 恢复能量
        if self.energy < self.max_energy:
            self.energy += 0.3
    
    def take_damage(self, damage):
        if self.hit_cooldown <= 0:
            self.hp -= damage
            self.hit_cooldown = 30
            if self.hp < 0:
                self.hp = 0
    
    def get_attack_rect(self):
        if self.is_attacking:
            if self.facing_right:
                return pygame.Rect(self.x + self.width, self.y + 30, 50, 40)
            else:
                return pygame.Rect(self.x - 50, self.y + 30, 50, 40)
        return None
    
    def draw(self, screen):
        # 眩晕效果
        if self.stunned and self.stun_timer % 10 < 5:
            alpha = 128
        else:
            alpha = 255
        
        # 绘制大头角色（像素风格）
        head_size = 60
        body_width = 40
        body_height = 40
        
        # 头部（大头）
        head_x = int(self.x + self.width//2 - head_size//2)
        head_y = int(self.y)
        pygame.draw.rect(screen, self.color, (head_x, head_y, head_size, head_size))
        pygame.draw.rect(screen, BLACK, (head_x, head_y, head_size, head_size), 3)
        
        # 眼睛
        eye_size = 8
        eye_y = head_y + 20
        if self.facing_right:
            left_eye_x = head_x + 15
            right_eye_x = head_x + 35
        else:
            left_eye_x = head_x + 25
            right_eye_x = head_x + 45
        
        pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), eye_size)
        pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (left_eye_x, eye_y), eye_size - 3)
        pygame.draw.circle(screen, BLACK, (right_eye_x, eye_y), eye_size - 3)
        
        # 嘴巴
        mouth_y = head_y + 45
        if self.is_attacking:
            pygame.draw.ellipse(screen, BLACK, 
                              (head_x + 20, mouth_y - 5, 20, 15))
        else:
            pygame.draw.arc(screen, BLACK, 
                          (head_x + 15, mouth_y - 10, 30, 20),
                          0, math.pi, 3)
        
        # 身体（小身体）
        body_x = int(self.x + self.width//2 - body_width//2)
        body_y = head_y + head_size
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_width, body_height))
        pygame.draw.rect(screen, BLACK, (body_x, body_y, body_width, body_height), 2)
        
        # 胳膊
        arm_y = body_y + 10
        if self.is_attacking:
            if self.facing_right:
                pygame.draw.line(screen, self.color, 
                               (body_x + body_width, arm_y), 
                               (body_x + body_width + 30, arm_y), 8)
            else:
                pygame.draw.line(screen, self.color, 
                               (body_x, arm_y), 
                               (body_x - 30, arm_y), 8)
        else:
            pygame.draw.line(screen, self.color, 
                           (body_x - 5, arm_y), 
                           (body_x - 5, arm_y + 20), 8)
            pygame.draw.line(screen, self.color, 
                           (body_x + body_width + 5, arm_y), 
                           (body_x + body_width + 5, arm_y + 20), 8)
        
        # 腿
        leg_y = body_y + body_height
        pygame.draw.line(screen, self.color, 
                       (body_x + 10, leg_y), 
                       (body_x + 10, leg_y + 20), 8)
        pygame.draw.line(screen, self.color, 
                       (body_x + body_width - 10, leg_y), 
                       (body_x + body_width - 10, leg_y + 20), 8)

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 35
        self.vel_y = 2
        self.type = random.choice(['damage', 'heal', 'stun', 'power'])
        self.active = True
        self.bounce = 0
        
        if self.type == 'damage':
            self.color = RED
            self.symbol = '💥'
        elif self.type == 'heal':
            self.color = GREEN
            self.symbol = '❤️'
        elif self.type == 'stun':
            self.color = PURPLE
            self.symbol = '⚡'
        else:
            self.color = GOLD
            self.symbol = '⭐'
    
    def update(self):
        self.y += self.vel_y
        self.bounce = math.sin(pygame.time.get_ticks() * 0.01) * 5
        if self.y > HEIGHT - 150:
            self.active = False
    
    def draw(self, screen):
        y_pos = int(self.y + self.bounce)
        # 外圈发光效果
        for i in range(3):
            pygame.draw.circle(screen, (*self.color, 100-i*30), 
                             (int(self.x), y_pos), self.size + i*3)
        pygame.draw.circle(screen, self.color, (int(self.x), y_pos), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), y_pos), self.size, 3)
        
        # 绘制符号
        text = font_medium.render(self.symbol, True, WHITE)
        text_rect = text.get_rect(center=(int(self.x), y_pos))
        screen.blit(text, text_rect)
    
    def apply_effect(self, player):
        if self.type == 'damage':
            player.take_damage(20)
        elif self.type == 'heal':
            player.hp = min(player.hp + 25, player.max_hp)
        elif self.type == 'stun':
            player.stunned = True
            player.stun_timer = 90
        else:
            player.energy = min(player.energy + 30, player.max_energy)

def draw_background(screen):
    # 天空渐变
    for y in range(HEIGHT - 150):
        ratio = y / (HEIGHT - 150)
        r = int(135 + (255 - 135) * ratio)
        g = int(206 + (200 - 206) * ratio)
        b = int(235 + (150 - 235) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # 远景建筑物（中国寺庙风格）
    # 左侧塔楼
    pygame.draw.rect(screen, DARK_BROWN, (100, 200, 80, 250))
    pygame.draw.polygon(screen, RED, [(90, 200), (140, 150), (190, 200)])
    pygame.draw.polygon(screen, ORANGE, [(85, 230), (140, 180), (195, 230)])
    
    # 右侧塔楼
    pygame.draw.rect(screen, DARK_BROWN, (WIDTH-180, 200, 80, 250))
    pygame.draw.polygon(screen, RED, [(WIDTH-190, 200), (WIDTH-140, 150), (WIDTH-90, 200)])
    pygame.draw.polygon(screen, ORANGE, [(WIDTH-195, 230), (WIDTH-140, 180), (WIDTH-85, 230)])
    
    # 中央大殿
    pygame.draw.rect(screen, LIGHT_BROWN, (WIDTH//2-150, 250, 300, 200))
    pygame.draw.polygon(screen, RED, [(WIDTH//2-170, 250), (WIDTH//2, 180), (WIDTH//2+170, 250)])
    
    # 装饰柱子
    for i in range(5):
        x = WIDTH//2 - 120 + i * 60
        pygame.draw.rect(screen, DARK_BROWN, (x, 300, 15, 150))

def draw_ground(screen):
    # 战斗场地
    ground_y = HEIGHT - 150
    
    # 地面纹理
    for i in range(0, WIDTH, 50):
        pygame.draw.rect(screen, (180, 150, 120), (i, ground_y, 48, 148))
        pygame.draw.rect(screen, (140, 110, 80), (i, ground_y, 48, 148), 2)
    
    # 中心圆形
    center_x = WIDTH // 2
    center_y = ground_y + 75
    pygame.draw.circle(screen, (200, 170, 140), (center_x, center_y), 150)
    pygame.draw.circle(screen, GOLD, (center_x, center_y), 150, 5)
    pygame.draw.circle(screen, (220, 190, 160), (center_x, center_y), 120)
    pygame.draw.circle(screen, GOLD, (center_x, center_y), 120, 3)

def draw_ui(screen, player1, player2, timer):
    # 玩家1 UI（左上）
    ui_y = 30
    
    # 玩家1名字
    p1_name = font_medium.render(player1.name, True, WHITE)
    pygame.draw.rect(screen, BLACK, (20, ui_y-5, p1_name.get_width()+20, 50))
    pygame.draw.rect(screen, player1.color, (20, ui_y-5, p1_name.get_width()+20, 50), 3)
    screen.blit(p1_name, (30, ui_y))
    
    # 血条
    hp_y = ui_y + 60
    hp_width = 350
    hp_height = 30
    pygame.draw.rect(screen, BLACK, (20, hp_y, hp_width+4, hp_height+4))
    pygame.draw.rect(screen, DARK_BROWN, (22, hp_y+2, hp_width, hp_height))
    hp1_fill = int((player1.hp / player1.max_hp) * hp_width)
    pygame.draw.rect(screen, RED, (22, hp_y+2, hp1_fill, hp_height))
    pygame.draw.rect(screen, player1.color, (22, hp_y+2, hp1_fill, hp_height), 3)
    
    # 能量条
    energy_y = hp_y + 40
    energy_width = 350
    energy_height = 15
    pygame.draw.rect(screen, BLACK, (20, energy_y, energy_width+4, energy_height+4))
    pygame.draw.rect(screen, DARK_BROWN, (22, energy_y+2, energy_width, energy_height))
    energy1_fill = int((player1.energy / player1.max_energy) * energy_width)
    pygame.draw.rect(screen, YELLOW, (22, energy_y+2, energy1_fill, energy_height))
    
    # 玩家2 UI（右上）
    p2_name = font_medium.render(player2.name, True, WHITE)
    p2_x = WIDTH - p2_name.get_width() - 50
    pygame.draw.rect(screen, BLACK, (p2_x-10, ui_y-5, p2_name.get_width()+20, 50))
    pygame.draw.rect(screen, player2.color, (p2_x-10, ui_y-5, p2_name.get_width()+20, 50), 3)
    screen.blit(p2_name, (p2_x, ui_y))
    
    # 血条
    hp2_x = WIDTH - 370 - 24
    pygame.draw.rect(screen, BLACK, (hp2_x, hp_y, hp_width+4, hp_height+4))
    pygame.draw.rect(screen, DARK_BROWN, (hp2_x+2, hp_y+2, hp_width, hp_height))
    hp2_fill = int((player2.hp / player2.max_hp) * hp_width)
    hp2_start = hp2_x + 2 + (hp_width - hp2_fill)
    pygame.draw.rect(screen, RED, (hp2_start, hp_y+2, hp2_fill, hp_height))
    pygame.draw.rect(screen, player2.color, (hp2_start, hp_y+2, hp2_fill, hp_height), 3)
    
    # 能量条
    pygame.draw.rect(screen, BLACK, (hp2_x, energy_y, energy_width+4, energy_height+4))
    pygame.draw.rect(screen, DARK_BROWN, (hp2_x+2, energy_y+2, energy_width, energy_height))
    energy2_fill = int((player2.energy / player2.max_energy) * energy_width)
    energy2_start = hp2_x + 2 + (energy_width - energy2_fill)
    pygame.draw.rect(screen, YELLOW, (energy2_start, energy_y+2, energy2_fill, energy_height))
    
    # 计时器（中央）
    timer_bg_size = 90
    timer_x = WIDTH // 2
    timer_y = 70
    pygame.draw.circle(screen, BLACK, (timer_x, timer_y), timer_bg_size//2 + 3)
    pygame.draw.circle(screen, (50, 50, 50), (timer_x, timer_y), timer_bg_size//2)
    pygame.draw.circle(screen, GOLD, (timer_x, timer_y), timer_bg_size//2, 4)
    
    timer_text = font_large.render(str(timer), True, YELLOW)
    timer_rect = timer_text.get_rect(center=(timer_x, timer_y))
    screen.blit(timer_text, timer_rect)

def main():
    clock = pygame.time.Clock()
    
    # 创建玩家
    player1_controls = {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'attack': pygame.K_SPACE
    }
    player2_controls = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'attack': pygame.K_RETURN
    }
    
    player1 = Player(250, HEIGHT - 250, BLUE, "GOKU", player1_controls)
    player2 = Player(WIDTH - 320, HEIGHT - 250, RED, "KRILLIN", player2_controls)
    
    bubbles = []
    bubble_timer = 0
    game_timer = 90
    frame_count = 0
    
    running = True
    game_over = False
    winner = None
    
    while running:
        clock.tick(FPS)
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    return
        
        if not game_over:
            keys = pygame.key.get_pressed()
            
            player1.update(keys)
            player2.update(keys)
            
            # 攻击检测
            if player1.is_attacking:
                attack_rect = player1.get_attack_rect()
                if attack_rect and attack_rect.colliderect(
                    pygame.Rect(player2.x, player2.y, player2.width, player2.height)):
                    player2.take_damage(15)
            
            if player2.is_attacking:
                attack_rect = player2.get_attack_rect()
                if attack_rect and attack_rect.colliderect(
                    pygame.Rect(player1.x, player1.y, player1.width, player1.height)):
                    player1.take_damage(15)
            
            # 生成泡泡
            bubble_timer += 1
            if bubble_timer >= BUBBLE_SPAWN_TIME:
                x = random.randint(200, WIDTH - 200)
                bubbles.append(Bubble(x, -50))
                bubble_timer = 0
            
            # 更新泡泡
            for bubble in bubbles[:]:
                bubble.update()
                if not bubble.active:
                    bubbles.remove(bubble)
                else:
                    p1_dist = math.sqrt((bubble.x - player1.x - player1.width//2)**2 + 
                                       (bubble.y - player1.y - player1.height//2)**2)
                    p2_dist = math.sqrt((bubble.x - player2.x - player2.width//2)**2 + 
                                       (bubble.y - player2.y - player2.height//2)**2)
                    
                    if p1_dist < 50:
                        bubble.apply_effect(player1)
                        bubbles.remove(bubble)
                    elif p2_dist < 50:
                        bubble.apply_effect(player2)
                        bubbles.remove(bubble)
            
            # 玩家碰撞
            if (abs(player1.x - player2.x) < 80 and 
                abs(player1.y - player2.y) < 100):
                if player1.x < player2.x:
                    player1.x -= 4
                    player2.x += 4
                else:
                    player1.x += 4
                    player2.x -= 4
            
            if frame_count % FPS == 0:
                game_timer -= 1
            
            if player1.hp <= 0:
                game_over = True
                winner = player2.name
            elif player2.hp <= 0:
                game_over = True
                winner = player1.name
            elif game_timer <= 0:
                game_over = True
                if player1.hp > player2.hp:
                    winner = player1.name
                elif player2.hp > player1.hp:
                    winner = player2.name
                else:
                    winner = "DRAW"
        
        # 绘制
        draw_background(screen)
        draw_ground(screen)
        
        # 绘制泡泡
        for bubble in bubbles:
            bubble.draw(screen)
        
        # 绘制玩家
        player1.draw(screen)
        player2.draw(screen)
        
        # 绘制UI
        draw_ui(screen, player1, player2, game_timer)
        
        # 游戏结束画面
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # READY文字效果
            ready_text = font_large.render("GAME OVER", True, GOLD)
            ready_shadow = font_large.render("GAME OVER", True, BLACK)
            ready_rect = ready_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            screen.blit(ready_shadow, (ready_rect.x + 4, ready_rect.y + 4))
            screen.blit(ready_text, ready_rect)
            
            if winner == "DRAW":
                win_text = font_large.render("平局!", True, YELLOW)
            else:
                win_text = font_large.render(f"{winner} 获胜!", True, YELLOW)
                # 皇冠
                crown_y = HEIGHT//2 - 30
                pygame.draw.polygon(screen, GOLD, [
                    (WIDTH//2-40, crown_y), (WIDTH//2-30, crown_y-20),
                    (WIDTH//2, crown_y-10), (WIDTH//2+30, crown_y-20),
                    (WIDTH//2+40, crown_y), (WIDTH//2+30, crown_y+10),
                    (WIDTH//2-30, crown_y+10)
                ])
            
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            win_shadow = font_large.render(win_text.get_text() if hasattr(win_text, 'get_text') else (f"{winner} 获胜!" if winner != "DRAW" else "平局!"), True, BLACK)
            screen.blit(win_shadow, (win_rect.x + 3, win_rect.y + 3))
            screen.blit(win_text, win_rect)
            
            restart_text = font_medium.render("按空格键重新开始", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    while True:
        main()
