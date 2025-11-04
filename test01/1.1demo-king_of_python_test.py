import pygame
import random
import math

# 初始化Pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King of Python - Demo Test 1.1")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
BLUE = (60, 120, 255)
ORANGE = (255, 150, 50)
GREEN = (80, 200, 80)
GRAY = (150, 150, 150)
BG_COLOR = (240, 240, 250)

# 游戏设置
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -15
MOVE_SPEED = 5
ATTACK_COOLDOWN = 30  # 攻击冷却时间（帧）
BUBBLE_SPAWN_TIME = 180  # 泡泡生成间隔（帧）

# 字体
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

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
        
        # 战斗相关
        self.has_pow_bubble = False
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_frame = 0
        self.knockback_x = 0
        
    def update(self, keys, platform):
        # 更新攻击状态
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame > 15:  # 攻击动画持续15帧
                self.is_attacking = False
                self.attack_frame = 0
        
        # 处理击退
        if abs(self.knockback_x) > 0.1:
            self.x += self.knockback_x
            self.knockback_x *= 0.8  # 击退衰减
        else:
            self.knockback_x = 0
        
        # 控制移动
        if keys[self.controls['left']] and not self.is_attacking:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        elif keys[self.controls['right']] and not self.is_attacking:
            self.vel_x = MOVE_SPEED
            self.facing_right = True
        else:
            self.vel_x = 0
        
        # 跳跃
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
        
        # 攻击
        if keys[self.controls['attack']] and self.attack_cooldown <= 0 and self.has_pow_bubble:
            self.is_attacking = True
            self.attack_cooldown = ATTACK_COOLDOWN
            self.has_pow_bubble = False
        
        # 应用重力
        self.vel_y += GRAVITY
        
        # 更新位置
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 平台碰撞检测
        self.on_ground = False
        if self.check_platform_collision(platform):
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
    
    def check_platform_collision(self, platform):
        return (self.x < platform['x'] + platform['width'] and
                self.x + self.width > platform['x'] and
                self.y < platform['y'] + platform['height'] and
                self.y + self.height > platform['y'])
    
    def get_attack_rect(self):
        """获取攻击判定区域"""
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
        """受到伤害"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        
        # 应用击退
        self.knockback_x = knockback_direction * 15
    
    def draw(self, screen):
        # 绘制角色方块
        if self.is_attacking and self.attack_frame % 4 < 2:
            # 攻击时闪烁效果
            color = (min(255, self.color[0] + 50), 
                    min(255, self.color[1] + 50), 
                    min(255, self.color[2] + 50))
        else:
            color = self.color
        
        pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))
        pygame.draw.rect(screen, BLACK, (int(self.x), int(self.y), self.width, self.height), 2)
        
        # 绘制眼睛
        eye_y = int(self.y + 15)
        if self.facing_right:
            left_eye = (int(self.x + 12), eye_y)
            right_eye = (int(self.x + 28), eye_y)
        else:
            left_eye = (int(self.x + 12), eye_y)
            right_eye = (int(self.x + 28), eye_y)
        
        pygame.draw.circle(screen, BLACK, left_eye, 4)
        pygame.draw.circle(screen, BLACK, right_eye, 4)
        
        # 如果有pow泡泡，显示指示器
        if self.has_pow_bubble:
            indicator_x = int(self.x + self.width // 2)
            indicator_y = int(self.y - 10)
            pygame.draw.circle(screen, ORANGE, (indicator_x, indicator_y), 5)
        
        # 绘制攻击判定区域（调试用）
        attack_rect = self.get_attack_rect()
        if attack_rect:
            pygame.draw.rect(screen, (255, 200, 0, 128), 
                           (attack_rect['x'], attack_rect['y'], 
                            attack_rect['width'], attack_rect['height']), 3)

class Bubble:
    def __init__(self, x, y, bubble_type='pow'):
        self.x = x
        self.y = y
        self.size = 25
        self.vel_y = 2
        self.type = bubble_type
        self.active = True
        self.color = ORANGE  # pow泡泡是橙色
        
    def update(self):
        self.y += self.vel_y
        if self.y > HEIGHT:
            self.active = False
    
    def draw(self, screen):
        # 绘制泡泡
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
        
        # 绘制"POW"文字
        text = font_small.render("POW", True, BLACK)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)
    
    def check_collision(self, player):
        """检测与玩家的碰撞"""
        dist = math.sqrt((self.x - (player.x + player.width//2))**2 + 
                        (self.y - (player.y + player.height//2))**2)
        return dist < self.size + player.width//2

def check_player_collision(player1, player2):
    """检测两个玩家之间的碰撞"""
    if (player1.x < player2.x + player2.width and
        player1.x + player1.width > player2.x and
        player1.y < player2.y + player2.height and
        player1.y + player1.height > player2.y):
        
        # 产生轻微击退
        if player1.x < player2.x:
            player1.x -= 2
            player2.x += 2
        else:
            player1.x += 2
            player2.x -= 2
        
        return True
    return False

def check_attack_hit(attacker, defender):
    """检测攻击是否命中"""
    attack_rect = attacker.get_attack_rect()
    if not attack_rect:
        return False
    
    # 检测defender是否在攻击范围内
    if (defender.x < attack_rect['x'] + attack_rect['width'] and
        defender.x + defender.width > attack_rect['x'] and
        defender.y < attack_rect['y'] + attack_rect['height'] and
        defender.y + defender.height > attack_rect['y']):
        return True
    return False

def draw_ui(screen, player1, player2):
    """绘制UI（血条等）"""
    # 血条设置
    hp_bar_width = 300
    hp_bar_height = 25
    hp_bar_y = 20
    
    # 玩家1血条（左侧）
    p1_x = 50
    pygame.draw.rect(screen, GRAY, (p1_x, hp_bar_y, hp_bar_width, hp_bar_height))
    hp1_width = int((player1.hp / player1.max_hp) * hp_bar_width)
    pygame.draw.rect(screen, player1.color, (p1_x, hp_bar_y, hp1_width, hp_bar_height))
    pygame.draw.rect(screen, BLACK, (p1_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
    
    # 玩家1名称
    p1_text = font_small.render("PLAYER 1", True, player1.color)
    screen.blit(p1_text, (p1_x, hp_bar_y - 25))
    
    # 玩家2血条（右侧）
    p2_x = WIDTH - 50 - hp_bar_width
    pygame.draw.rect(screen, GRAY, (p2_x, hp_bar_y, hp_bar_width, hp_bar_height))
    hp2_width = int((player2.hp / player2.max_hp) * hp_bar_width)
    pygame.draw.rect(screen, player2.color, (p2_x, hp_bar_y, hp2_width, hp_bar_height))
    pygame.draw.rect(screen, BLACK, (p2_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
    
    # 玩家2名称
    p2_text = font_small.render("PLAYER 2", True, player2.color)
    p2_text_rect = p2_text.get_rect(right=p2_x + hp_bar_width, top=hp_bar_y - 25)
    screen.blit(p2_text, p2_text_rect)

def draw_platform(screen, platform):
    """绘制平台"""
    # 绘制阴影
    pygame.draw.rect(screen, (100, 100, 100), 
                    (platform['x'] + 3, platform['y'] + 3, 
                     platform['width'], platform['height']))
    # 绘制平台
    pygame.draw.rect(screen, GREEN, 
                    (platform['x'], platform['y'], 
                     platform['width'], platform['height']))
    pygame.draw.rect(screen, (60, 160, 60), 
                    (platform['x'], platform['y'], 
                     platform['width'], platform['height']), 3)

def main():
    clock = pygame.time.Clock()
    
    # 创建平台
    platform = {
        'x': WIDTH // 2 - 200,
        'y': HEIGHT - 150,
        'width': 400,
        'height': 20
    }
    
    # 创建玩家
    player1_controls = {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'jump': pygame.K_w,
        'attack': pygame.K_f
    }
    player2_controls = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP,
        'attack': pygame.K_l
    }
    
    player1 = Player(250, 200, BLUE, player1_controls, facing_right=True)
    player2 = Player(500, 200, RED, player2_controls, facing_right=False)
    
    bubbles = []
    bubble_timer = 0
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
            player1.update(keys, platform)
            player2.update(keys, platform)
            
            # 检测玩家之间的碰撞
            check_player_collision(player1, player2)
            
            # 检测攻击命中
            if player1.is_attacking and player1.attack_frame == 5:  # 攻击生效帧
                if check_attack_hit(player1, player2):
                    knockback_dir = 1 if player1.facing_right else -1
                    player2.take_damage(3, knockback_dir)
            
            if player2.is_attacking and player2.attack_frame == 5:
                if check_attack_hit(player2, player1):
                    knockback_dir = 1 if player2.facing_right else -1
                    player1.take_damage(3, knockback_dir)
            
            # 生成泡泡
            bubble_timer += 1
            if bubble_timer >= BUBBLE_SPAWN_TIME:
                x = random.randint(100, WIDTH - 100)
                bubbles.append(Bubble(x, -50, 'pow'))
                bubble_timer = 0
            
            # 更新泡泡
            for bubble in bubbles[:]:
                bubble.update()
                if not bubble.active:
                    bubbles.remove(bubble)
                else:
                    # 检测玩家拾取泡泡
                    if bubble.check_collision(player1) and not player1.has_pow_bubble:
                        player1.has_pow_bubble = True
                        bubbles.remove(bubble)
                    elif bubble.check_collision(player2) and not player2.has_pow_bubble:
                        player2.has_pow_bubble = True
                        bubbles.remove(bubble)
            
            # 检查游戏结束条件
            if player1.hp <= 0:
                game_over = True
                winner = "PLAYER 2"
            elif player2.hp <= 0:
                game_over = True
                winner = "PLAYER 1"
        
        # 绘制
        screen.fill(BG_COLOR)
        
        # 绘制平台
        draw_platform(screen, platform)
        
        # 绘制泡泡
        for bubble in bubbles:
            bubble.draw(screen)
        
        # 绘制玩家
        player1.draw(screen)
        player2.draw(screen)
        
        # 绘制UI
        draw_ui(screen, player1, player2)
        
        # 游戏结束画面
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            win_text = font_large.render(f"{winner} WINS!", True, ORANGE)
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(win_text, win_rect)
            
            restart_text = font_medium.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    while True:
        main()
