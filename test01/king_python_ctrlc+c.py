import pygame
import sys
import os
import time
import random
import math

# 初始化Pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King of Python - Demo Test 1.1 (develop copy)")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
BLUE = (60, 120, 255)
ORANGE = (255, 150, 50)
GREEN = (80, 200, 80)
GRAY = (150, 150, 150)
CYAN = (0, 255, 255)
PURPLE = (160, 32, 240)
YELLOW = (255, 215, 0)
ICE_BLUE = (173, 216, 230)
BG_COLOR = (240, 240, 250)

# 游戏设置
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -15
MOVE_SPEED = 5
ATTACK_COOLDOWN = 30
BUBBLE_SPAWN_TIME = 150
FREEZE_DURATION = 180
PROJECTILE_SPEED = 8

# 字体
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)
font_tiny = pygame.font.Font(None, 24)
font_bubble = pygame.font.Font(None, 20)  # 统一的泡泡字体

# Avatar surfaces
p1_avatar_surf = None
p2_avatar_surf = None

try:
    HERE = os.path.dirname(__file__)
    REPO_ROOT = os.path.abspath(HERE)
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from King_Monica.face_login_demo import capture_and_make_sprite
except Exception:
    capture_and_make_sprite = None

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
        
        # 技能状态
        self.skill = None  # 可以是 'pow', 'delete', 'print', None
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_power = 3
        self.knockback_x = 0
        
        # 冻结状态
        self.is_frozen = False
        self.freeze_timer = 0
        
    def update(self, keys, platform):
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
            if self.check_platform_collision(platform):
                if self.vel_y > 0:
                    self.y = platform['y'] - self.height
                    self.vel_y = 0
                    self.on_ground = True
            
            return
        
        # 更新攻击状态
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame > 15:
                self.is_attacking = False
                self.attack_frame = 0
        
        # 处理击退
        if abs(self.knockback_x) > 0.1:
            self.x += self.knockback_x
            self.knockback_x *= 0.8
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
        
        # 应用重力
        self.vel_y += GRAVITY
        
        # 更新位置
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 平台碰撞检测
        self.on_ground = False
        if self.check_platform_collision(platform):
            if self.vel_y > 0:
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
    
    def use_skill(self):
        """使用技能并返回技能类型"""
        if self.skill and self.attack_cooldown <= 0:
            used_skill = self.skill
            self.skill = None
            self.attack_cooldown = ATTACK_COOLDOWN
            
            # pow 和 delete 需要攻击动画
            if used_skill in ['pow', 'delete']:
                self.is_attacking = True
                self.attack_frame = 0
            
            return used_skill
        return None
    
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
        self.knockback_x = knockback_direction * 15
    
    def freeze(self):
        """冻结玩家"""
        self.is_frozen = True
        self.freeze_timer = FREEZE_DURATION
        self.vel_x = 0
    
    def draw(self, screen):
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
            # 正常状态
            if self.is_attacking and self.attack_frame % 4 < 2:
                color = (min(255, self.color[0] + 50), 
                        min(255, self.color[1] + 50), 
                        min(255, self.color[2] + 50))
            else:
                color = self.color
            
            pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))
            pygame.draw.rect(screen, BLACK, (int(self.x), int(self.y), self.width, self.height), 2)
        
        # 绘制眼睛
        eye_y = int(self.y + 15)
        left_eye = (int(self.x + 12), eye_y)
        right_eye = (int(self.x + 28), eye_y)
        
        eye_color = CYAN if self.is_frozen else BLACK
        pygame.draw.circle(screen, eye_color, left_eye, 4)
        pygame.draw.circle(screen, eye_color, right_eye, 4)
        
        # 显示持有的技能
        if self.skill and not self.is_frozen:
            indicator_x = int(self.x + self.width // 2)
            indicator_y = int(self.y - 15)
            
            # 根据技能类型显示不同颜色的指示器
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
        
        # 绘制攻击判定区域
        attack_rect = self.get_attack_rect()
        if attack_rect and not self.is_frozen:
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
        
        # 根据类型设置颜色
        if self.type == 'pow':
            self.color = ORANGE
        elif self.type == 'delete':
            self.color = RED
        elif self.type == 'print':
            self.color = YELLOW
        elif self.type == 'ctrlc':
            self.color = CYAN
        else:
            self.color = GRAY
        
    def update(self):
        self.y += self.vel_y
        if self.y > HEIGHT:
            self.active = False
    
    def draw(self, screen):
        # 绘制泡泡
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
        
        # 统一的字体和颜色配置
        text_color = BLACK  # 所有泡泡文字都用黑色
        
        # 绘制类型标识
        if self.type == 'pow':
            label = 'pow()'
        elif self.type == 'delete':
            label = 'delete'
        elif self.type == 'print':
            label = 'print'
        elif self.type == 'ctrlc':
            label = 'Ctrl+C'
        else:
            label = ''

        if label:
            text = font_bubble.render(label, True, text_color)
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(text, text_rect)
        
        # Ctrl+C 泡泡的冰晶特效
        if self.type == 'ctrlc':
            if pygame.time.get_ticks() % 500 < 250:
                for angle in range(0, 360, 90):
                    rad = math.radians(angle)
                    spark_x = int(self.x + math.cos(rad) * (self.size + 5))
                    spark_y = int(self.y + math.sin(rad) * (self.size + 5))
                    pygame.draw.circle(screen, WHITE, (spark_x, spark_y), 3)
    
    def check_collision(self, player):
        """检测与玩家的碰撞"""
        dist = math.sqrt((self.x - (player.x + player.width//2))**2 + 
                        (self.y - (player.y + player.height//2))**2)
        return dist < self.size + player.width//2

class Projectile:
    """飞行道具类 - 用于print技能"""
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.owner = owner
        self.vel_x = PROJECTILE_SPEED * direction
        self.active = True
        self.damage = 2
        self.text = "Attack!"
        
    def update(self):
        self.x += self.vel_x
        
        # 超出屏幕边界
        if self.x < -50 or self.x > WIDTH + 50:
            self.active = False
    
    def draw(self, screen):
        # 绘制飞行的字符串
        text = font_small.render(self.text, True, YELLOW)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        
        # 添加发光效果
        glow_text = font_small.render(self.text, True, (255, 255, 200))
        glow_rect = glow_text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(glow_text, (glow_rect.x + 2, glow_rect.y + 2))
        screen.blit(text, text_rect)
    
    def check_collision(self, player):
        """检测是否击中玩家"""
        if player == self.owner:
            return False
        
        # 简单的矩形碰撞检测
        proj_rect = pygame.Rect(self.x - 30, self.y - 15, 60, 30)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        return proj_rect.colliderect(player_rect)

def check_player_collision(player1, player2):
    """检测两个玩家之间的碰撞"""
    if (player1.x < player2.x + player2.width and
        player1.x + player1.width > player2.x and
        player1.y < player2.y + player2.height and
        player1.y + player1.height > player2.y):
        
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
    
    if (defender.x < attack_rect['x'] + attack_rect['width'] and
        defender.x + defender.width > attack_rect['x'] and
        defender.y < attack_rect['y'] + attack_rect['height'] and
        defender.y + defender.height > attack_rect['y']):
        return True
    return False

def load_avatar_surface(path, max_display=80):
    try:
        surf = pygame.image.load(path).convert_alpha()
    except Exception:
        return None
    w, h = surf.get_size()
    if max(w, h) > max_display:
        scale = max_display / max(w, h)
        surf = pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))
    return surf

def draw_ui(screen, player1, player2, p1_avatar=None, p2_avatar=None):
    """绘制UI（血条等）"""
    hp_bar_width = 300
    hp_bar_height = 25
    hp_bar_y = 60
    
    # 玩家1血条
    p1_x = 50
    pygame.draw.rect(screen, GRAY, (p1_x, hp_bar_y, hp_bar_width, hp_bar_height))
    hp1_width = int((player1.hp / player1.max_hp) * hp_bar_width)
    pygame.draw.rect(screen, player1.color, (p1_x, hp_bar_y, hp1_width, hp_bar_height))
    pygame.draw.rect(screen, BLACK, (p1_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
    
    name1 = "PLAYER 1"
    p1_text = font_small.render(name1, True, player1.color)
    if p1_text.get_width() > hp_bar_width:
        small_font = pygame.font.Font(None, 20)
        p1_text = small_font.render(name1, True, player1.color)
    p1_text_rect = p1_text.get_rect(center=(p1_x + hp_bar_width // 2, hp_bar_y - 12))
    screen.blit(p1_text, p1_text_rect)
    
    if p1_avatar:
        aw = p1_avatar.get_width()
        ah = p1_avatar.get_height()
        ax = p1_x - aw - 8
        ay = hp_bar_y + (hp_bar_height // 2) - (ah // 2)
        if ax < 8:
            ax = 8
        if ay < 8:
            ay = 8
        screen.blit(p1_avatar, (ax, ay))
    
    # 玩家2血条
    p2_x = WIDTH - 50 - hp_bar_width
    pygame.draw.rect(screen, GRAY, (p2_x, hp_bar_y, hp_bar_width, hp_bar_height))
    hp2_width = int((player2.hp / player2.max_hp) * hp_bar_width)
    pygame.draw.rect(screen, player2.color, (p2_x, hp_bar_y, hp2_width, hp_bar_height))
    pygame.draw.rect(screen, BLACK, (p2_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
    
    name2 = "PLAYER 2"
    p2_text = font_small.render(name2, True, player2.color)
    if p2_text.get_width() > hp_bar_width:
        small_font = pygame.font.Font(None, 20)
        p2_text = small_font.render(name2, True, player2.color)
    p2_text_rect = p2_text.get_rect(center=(p2_x + hp_bar_width // 2, hp_bar_y - 12))
    screen.blit(p2_text, p2_text_rect)
    
    if p2_avatar:
        aw = p2_avatar.get_width()
        ah = p2_avatar.get_height()
        ax = p2_x + hp_bar_width + 8
        ay = hp_bar_y + (hp_bar_height // 2) - (ah // 2)
        if ax + aw > WIDTH - 8:
            ax = WIDTH - aw - 8
        if ay < 8:
            ay = 8
        screen.blit(p2_avatar, (ax, ay))
    
    # 绘制技能说明
    info_y = HEIGHT - 100
    pow_info = font_tiny.render("pow(): Attack 8HP", True, ORANGE)
    delete_info = font_tiny.render("delete: Remove enemy skill", True, RED)
    print_info = font_tiny.render("print: Shoot 'Attack!' 2HP", True, YELLOW)
    ctrlc_info = font_tiny.render("Ctrl+C: Freeze 3s", True, CYAN)
    
    screen.blit(pow_info, (WIDTH//2 - 130, info_y))
    screen.blit(delete_info, (WIDTH//2 - 130, info_y + 22))
    screen.blit(print_info, (WIDTH//2 - 130, info_y + 44))
    screen.blit(ctrlc_info, (WIDTH//2 - 130, info_y + 66))

def draw_platform(screen, platform):
    """绘制平台"""
    pygame.draw.rect(screen, (100, 100, 100), 
                    (platform['x'] + 3, platform['y'] + 3, 
                     platform['width'], platform['height']))
    pygame.draw.rect(screen, GREEN, 
                    (platform['x'], platform['y'], 
                     platform['width'], platform['height']))
    pygame.draw.rect(screen, (60, 160, 60), 
                    (platform['x'], platform['y'], 
                     platform['width'], platform['height']), 3)

def main():
    clock = pygame.time.Clock()
    start = True
    local_p1 = None
    local_p2 = None
    
    while start:
        screen.fill(BG_COLOR)
        title = font_large.render('King of Python', True, BLACK)
        sub = font_small.render('Press C to capture faces, S to skip and start', True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))
        pygame.display.flip()
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c and capture_and_make_sprite is not None:
                    p1 = capture_and_make_sprite('Face1')
                    time.sleep(1.0)
                    p2 = capture_and_make_sprite('Face2')
                    local_p1 = load_avatar_surface(p1)
                    local_p2 = load_avatar_surface(p2)
                    start = False
                if ev.key == pygame.K_s:
                    start = False
    
    # 创建平台
    left_margin = 50
    right_margin = 50
    platform = {
        'x': left_margin,
        'y': HEIGHT - 150,
        'width': WIDTH - left_margin - right_margin,
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
    projectiles = []
    bubble_timer = 0
    
    running = True
    game_over = False
    winner = None
    
    # 技能使用状态追踪
    last_p1_skill = None
    last_p2_skill = None
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    return
                
                # 技能释放（单次按键检测）
                if not game_over:
                    if event.key == player1.controls['attack']:
                        skill_used = player1.use_skill()
                        if skill_used:
                            last_p1_skill = skill_used
                            if skill_used == 'print':
                                # 发射飞行道具
                                proj_x = player1.x + player1.width if player1.facing_right else player1.x
                                proj_y = player1.y + player1.height // 2
                                direction = 1 if player1.facing_right else -1
                                projectiles.append(Projectile(proj_x, proj_y, direction, player1))
                    
                    if event.key == player2.controls['attack']:
                        skill_used = player2.use_skill()
                        if skill_used:
                            last_p2_skill = skill_used
                            if skill_used == 'print':
                                proj_x = player2.x + player2.width if player2.facing_right else player2.x
                                proj_y = player2.y + player2.height // 2
                                direction = 1 if player2.facing_right else -1
                                projectiles.append(Projectile(proj_x, proj_y, direction, player2))
        
        if not game_over:
            keys = pygame.key.get_pressed()
            
            # 更新玩家
            player1.update(keys, platform)
            player2.update(keys, platform)
            
            # 检测玩家碰撞
            check_player_collision(player1, player2)
            
            # 检测pow攻击命中
            if player1.is_attacking and player1.attack_frame == 5 and not player1.is_frozen:
                if last_p1_skill == 'pow' and check_attack_hit(player1, player2):
                    knockback_dir = 1 if player1.facing_right else -1
                    player2.take_damage(8, knockback_dir)
                    last_p1_skill = None
                elif last_p1_skill == 'delete' and check_attack_hit(player1, player2):
                    # delete技能：消除对方的技能
                    player2.skill = None
                    last_p1_skill = None
            
            if player2.is_attacking and player2.attack_frame == 5 and not player2.is_frozen:
                if last_p2_skill == 'pow' and check_attack_hit(player2, player1):
                    knockback_dir = 1 if player2.facing_right else -1
                    player1.take_damage(8, knockback_dir)
                    last_p2_skill = None
                elif last_p2_skill == 'delete' and check_attack_hit(player2, player1):
                    player1.skill = None
                    last_p2_skill = None
            
            # 更新飞行道具
            for proj in projectiles[:]:
                proj.update()
                if not proj.active:
                    projectiles.remove(proj)
                else:
                    # 检测飞行道具击中
                    if proj.check_collision(player1) and proj.owner != player1:
                        knockback = 10 if proj.direction > 0 else -10
                        player1.take_damage(proj.damage, knockback)
                        projectiles.remove(proj)
                    elif proj.check_collision(player2) and proj.owner != player2:
                        knockback = 10 if proj.direction > 0 else -10
                        player2.take_damage(proj.damage, knockback)
                        projectiles.remove(proj)
            
            # 生成泡泡
            bubble_timer += 1
            if bubble_timer >= BUBBLE_SPAWN_TIME:
                x = random.randint(100, WIDTH - 100)
                # 泡泡生成概率：pow 30%, delete 20%, print 30%, ctrlc 20%
                rand = random.random()
                if rand < 0.3:
                    btype = 'pow'
                elif rand < 0.5:
                    btype = 'delete'
                elif rand < 0.8:
                    btype = 'print'
                else:
                    btype = 'ctrlc'
                bubbles.append(Bubble(x, -50, btype))
                bubble_timer = 0
            
            # 更新泡泡
            for bubble in bubbles[:]:
                bubble.update()
                if not bubble.active:
                    bubbles.remove(bubble)
                else:
                    # player1拾取
                    if bubble.check_collision(player1):
                        if bubble.type in ['pow', 'delete', 'print'] and player1.skill is None:
                            player1.skill = bubble.type
                        elif bubble.type == 'ctrlc':
                            player1.freeze()
                        bubbles.remove(bubble)
                        continue

                    # player2拾取
                    if bubble.check_collision(player2):
                        if bubble.type in ['pow', 'delete', 'print'] and player2.skill is None:
                            player2.skill = bubble.type
                        elif bubble.type == 'ctrlc':
                            player2.freeze()
                        bubbles.remove(bubble)
            
            # 检查游戏结束
            if player1.hp <= 0:
                game_over = True
                winner = "PLAYER 2"
            elif player2.hp <= 0:
                game_over = True
                winner = "PLAYER 1"
        
        # 绘制
        screen.fill(BG_COLOR)
        draw_platform(screen, platform)
        
        # 绘制泡泡
        for bubble in bubbles:
            bubble.draw(screen)
        
        # 绘制飞行道具
        for proj in projectiles:
            proj.draw(screen)
        
        # 绘制玩家
        player1.draw(screen)
        player2.draw(screen)
        
        # 绘制UI
        draw_ui(screen, player1, player2, p1_avatar=local_p1, p2_avatar=local_p2)
        
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
