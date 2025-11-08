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
RED = (255, 60, 60)
BLUE = (60, 120, 255)
YELLOW = (255, 220, 0)
GREEN = (80, 200, 80)
ORANGE = (255, 150, 50)
PURPLE = (180, 80, 255)
BG_COLOR = (250, 240, 200)

# 游戏设置
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -15
MOVE_SPEED = 6
BUBBLE_SPAWN_TIME = 120  # 帧数

# 字体
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.hp = 100
        self.max_hp = 100
        self.on_ground = False
        self.facing_right = True
        self.controls = controls
        self.stunned = False
        self.stun_timer = 0
        self.hit_cooldown = 0
        
    def update(self, keys, platforms):
        # 处理眩晕状态
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        # 控制移动（除非被眩晕）
        if not self.stunned:
            if keys[self.controls['left']]:
                self.vel_x = -MOVE_SPEED
                self.facing_right = False
            elif keys[self.controls['right']]:
                self.vel_x = MOVE_SPEED
                self.facing_right = True
            else:
                self.vel_x = 0
            
            # 跳跃
            if keys[self.controls['jump']] and self.on_ground:
                self.vel_y = JUMP_POWER
                self.on_ground = False
        else:
            self.vel_x *= 0.9  # 眩晕时减速
        
        # 应用重力
        self.vel_y += GRAVITY
        
        # 更新位置
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 地面碰撞检测
        self.on_ground = False
        for platform in platforms:
            if self.check_collision(platform):
                if self.vel_y > 0:  # 向下移动
                    self.y = platform['y'] - self.height
                    self.vel_y = 0
                    self.on_ground = True
        
        # 边界限制
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
        
        # 掉出场外判定
        if self.y > HEIGHT:
            self.hp = 0
    
    def check_collision(self, platform):
        return (self.x < platform['x'] + platform['width'] and
                self.x + self.width > platform['x'] and
                self.y < platform['y'] + platform['height'] and
                self.y + self.height > platform['y'])
    
    def take_damage(self, damage):
        if self.hit_cooldown <= 0:
            self.hp -= damage
            self.hit_cooldown = 30
            if self.hp < 0:
                self.hp = 0
    
    def draw(self, screen):
        # 眩晕效果
        if self.stunned and self.stun_timer % 10 < 5:
            color = (self.color[0]//2, self.color[1]//2, self.color[2]//2)
        else:
            color = self.color
        
        # 绘制身体（大头角色）
        head_radius = self.width // 2
        pygame.draw.circle(screen, color, 
                         (int(self.x + self.width//2), int(self.y + head_radius)), 
                         head_radius)
        
        # 绘制眼睛
        eye_y = int(self.y + head_radius - 5)
        if self.facing_right:
            left_eye = (int(self.x + self.width//2 - 10), eye_y)
            right_eye = (int(self.x + self.width//2 + 10), eye_y)
        else:
            left_eye = (int(self.x + self.width//2 - 10), eye_y)
            right_eye = (int(self.x + self.width//2 + 10), eye_y)
        
        pygame.draw.circle(screen, WHITE, left_eye, 8)
        pygame.draw.circle(screen, WHITE, right_eye, 8)
        pygame.draw.circle(screen, BLACK, left_eye, 4)
        pygame.draw.circle(screen, BLACK, right_eye, 4)
        
        # 绘制嘴巴
        mouth_y = int(self.y + head_radius + 10)
        pygame.draw.arc(screen, BLACK, 
                       (int(self.x + self.width//2 - 15), mouth_y - 10, 30, 20),
                       0, math.pi, 2)
        
        # 绘制小身体
        body_y = int(self.y + self.height - 30)
        pygame.draw.rect(screen, color, 
                        (int(self.x + self.width//2 - 10), body_y, 20, 30))

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.vel_y = 2
        self.type = random.choice(['damage', 'heal', 'stun', 'speed'])
        self.active = True
        
        # 设置泡泡颜色和效果
        if self.type == 'damage':
            self.color = RED
            self.symbol = 'DMG'
        elif self.type == 'heal':
            self.color = GREEN
            self.symbol = 'HP+'
        elif self.type == 'stun':
            self.color = PURPLE
            self.symbol = 'ZZZ'
        else:
            self.color = YELLOW
            self.symbol = 'SPD'
    
    def update(self):
        self.y += self.vel_y
        if self.y > HEIGHT:
            self.active = False
    
    def draw(self, screen):
        # 绘制泡泡
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
        
        # 绘制符号
        text = font_small.render(self.symbol, True, BLACK)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)
    
    def apply_effect(self, player):
        if self.type == 'damage':
            player.take_damage(15)
        elif self.type == 'heal':
            player.hp = min(player.hp + 20, player.max_hp)
        elif self.type == 'stun':
            player.stunned = True
            player.stun_timer = 60
        else:  # speed
            pass  # 速度提升效果可以添加

def draw_ui(screen, player1, player2, timer):
    # 绘制血条背景
    hp_bar_width = 400
    hp_bar_height = 30
    
    # 玩家1血条（左侧）
    pygame.draw.rect(screen, BLACK, (50, 30, hp_bar_width + 4, hp_bar_height + 4))
    pygame.draw.rect(screen, RED, (52, 32, hp_bar_width, hp_bar_height))
    hp1_width = int((player1.hp / player1.max_hp) * hp_bar_width)
    pygame.draw.rect(screen, player1.color, (52, 32, hp1_width, hp_bar_height))
    
    # 玩家2血条（右侧）
    p2_x = WIDTH - 50 - hp_bar_width
    pygame.draw.rect(screen, BLACK, (p2_x - 2, 30, hp_bar_width + 4, hp_bar_height + 4))
    pygame.draw.rect(screen, RED, (p2_x, 32, hp_bar_width, hp_bar_height))
    hp2_width = int((player2.hp / player2.max_hp) * hp_bar_width)
    pygame.draw.rect(screen, player2.color, (p2_x, 32, hp2_width, hp_bar_height))
    
    # 玩家名称
    p1_text = font_small.render("PLAYER 1", True, BLACK)
    screen.blit(p1_text, (52, 5))
    p2_text = font_small.render("PLAYER 2", True, BLACK)
    screen.blit(p2_text, (p2_x, 5))
    
    # 计时器
    timer_text = font_large.render(str(timer), True, YELLOW)
    timer_rect = timer_text.get_rect(center=(WIDTH//2, 50))
    pygame.draw.circle(screen, BLACK, (WIDTH//2, 50), 40)
    pygame.draw.circle(screen, GREEN, (WIDTH//2, 50), 38)
    screen.blit(timer_text, timer_rect)

def draw_platforms(screen, platforms):
    for platform in platforms:
        # 绘制平台阴影
        pygame.draw.rect(screen, (150, 100, 50), 
                        (platform['x'] + 3, platform['y'] + 3, 
                         platform['width'], platform['height']))
        # 绘制平台
        pygame.draw.rect(screen, ORANGE, 
                        (platform['x'], platform['y'], 
                         platform['width'], platform['height']))
        pygame.draw.rect(screen, (200, 130, 70), 
                        (platform['x'], platform['y'], 
                         platform['width'], platform['height']), 3)

def main():
    clock = pygame.time.Clock()
    
    # 创建平台
    platforms = [
        {'x': 0, 'y': HEIGHT - 50, 'width': WIDTH, 'height': 50},  # 地面
        {'x': 200, 'y': HEIGHT - 200, 'width': 200, 'height': 20},  # 左平台
        {'x': WIDTH - 400, 'y': HEIGHT - 200, 'width': 200, 'height': 20},  # 右平台
        {'x': WIDTH//2 - 100, 'y': HEIGHT - 350, 'width': 200, 'height': 20},  # 中央平台
    ]
    
    # 创建玩家
    player1_controls = {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'jump': pygame.K_w
    }
    player2_controls = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP
    }
    
    player1 = Player(200, 300, BLUE, player1_controls)
    player2 = Player(WIDTH - 250, 300, RED, player2_controls)
    
    bubbles = []
    bubble_timer = 0
    game_timer = 90  # 90秒
    frame_count = 0
    
    running = True
    game_over = False
    winner = None
    
    while running:
        clock.tick(FPS)
        frame_count += 1
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    return  # 重新开始
        
        if not game_over:
            keys = pygame.key.get_pressed()
            
            # 更新玩家
            player1.update(keys, platforms)
            player2.update(keys, platforms)
            
            # 生成泡泡
            bubble_timer += 1
            if bubble_timer >= BUBBLE_SPAWN_TIME:
                x = random.randint(100, WIDTH - 100)
                bubbles.append(Bubble(x, -50))
                bubble_timer = 0
            
            # 更新泡泡
            for bubble in bubbles[:]:
                bubble.update()
                if not bubble.active:
                    bubbles.remove(bubble)
                else:
                    # 检测玩家拾取泡泡
                    p1_dist = math.sqrt((bubble.x - player1.x - player1.width//2)**2 + 
                                       (bubble.y - player1.y - player1.height//2)**2)
                    p2_dist = math.sqrt((bubble.x - player2.x - player2.width//2)**2 + 
                                       (bubble.y - player2.y - player2.height//2)**2)
                    
                    if p1_dist < player1.width:
                        bubble.apply_effect(player1)
                        bubbles.remove(bubble)
                    elif p2_dist < player2.width:
                        bubble.apply_effect(player2)
                        bubbles.remove(bubble)
            
            # 玩家碰撞检测
            if (abs(player1.x - player2.x) < 50 and 
                abs(player1.y - player2.y) < 80):
                # 互相推开
                if player1.x < player2.x:
                    player1.x -= 3
                    player2.x += 3
                else:
                    player1.x += 3
                    player2.x -= 3
            
            # 更新游戏计时器
            if frame_count % FPS == 0:
                game_timer -= 1
            
            # 检查游戏结束条件
            if player1.hp <= 0:
                game_over = True
                winner = "PLAYER 2"
            elif player2.hp <= 0:
                game_over = True
                winner = "PLAYER 1"
            elif game_timer <= 0:
                game_over = True
                if player1.hp > player2.hp:
                    winner = "PLAYER 1"
                elif player2.hp > player1.hp:
                    winner = "PLAYER 2"
                else:
                    winner = "DRAW"
        
        # 绘制
        screen.fill(BG_COLOR)
        
        # 绘制背景装饰
        for i in range(5):
            pygame.draw.circle(screen, (220, 210, 180), 
                             (random.randint(0, WIDTH), random.randint(0, HEIGHT//2)), 
                             random.randint(30, 80), 1)
        
        # 绘制平台
        draw_platforms(screen, platforms)
        
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
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            if winner == "DRAW":
                win_text = font_large.render("平局!", True, YELLOW)
            else:
                win_text = font_large.render(f"{winner} 获胜!", True, YELLOW)
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(win_text, win_rect)
            
            restart_text = font_medium.render("按空格键重新开始", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    while True:
        main()
