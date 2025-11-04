import pygame
import random
import sys

# 初始化
pygame.init()

# 常量
WIDTH, HEIGHT = 800, 600
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 140, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

# 游戏设置
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5
KNOCKBACK_FORCE = 20

class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = color
        self.vx = 0
        self.vy = 0
        self.hp = 100
        self.max_hp = 100
        self.on_ground = False
        self.controls = controls  # {'left': K_a, 'right': K_d, 'jump': K_w, 'attack': K_SPACE}
        self.has_bubble = False
        self.facing_right = True
        
    def update(self, keys, platforms):
        # 移动控制
        self.vx = 0
        if keys[self.controls['left']]:
            self.vx = -MOVE_SPEED
            self.facing_right = False
        if keys[self.controls['right']]:
            self.vx = MOVE_SPEED
            self.facing_right = True
            
        # 跳跃
        if keys[self.controls['jump']] and self.on_ground:
            self.vy = JUMP_STRENGTH
            self.on_ground = False
        
        # 应用重力
        self.vy += GRAVITY
        
        # 更新位置
        self.x += self.vx
        self.y += self.vy
        
        # 地面碰撞
        self.on_ground = False
        for platform in platforms:
            if self.collide_with_platform(platform):
                self.on_ground = True
                self.vy = 0
                self.y = platform['y'] - self.height
        
        # 边界检测
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
            
    def collide_with_platform(self, platform):
        if (self.x + self.width > platform['x'] and 
            self.x < platform['x'] + platform['width'] and
            self.y + self.height >= platform['y'] and
            self.y + self.height <= platform['y'] + 20 and
            self.vy >= 0):
            return True
        return False
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage, knockback_x):
        self.hp -= damage
        self.vx = knockback_x
        self.vy = -10
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # 绘制方向指示（小三角形）
        if self.facing_right:
            points = [(self.x + self.width, self.y + self.height//2),
                     (self.x + self.width + 10, self.y + self.height//2 - 5),
                     (self.x + self.width + 10, self.y + self.height//2 + 5)]
        else:
            points = [(self.x, self.y + self.height//2),
                     (self.x - 10, self.y + self.height//2 - 5),
                     (self.x - 10, self.y + self.height//2 + 5)]
        pygame.draw.polygon(screen, self.color, points)
        
        # 如果有泡泡，显示指示器
        if self.has_bubble:
            pygame.draw.circle(screen, ORANGE, 
                             (int(self.x + self.width//2), int(self.y - 15)), 8)

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.color = ORANGE
        self.vy = 2
        
    def update(self):
        self.y += self.vy
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # 绘制 "pow()" 文字
        font = pygame.font.Font(None, 20)
        text = font.render("pow", True, WHITE)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class AttackZone:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 60
        self.direction = direction
        self.lifetime = 15  # 帧数
        self.damage = 3
        
    def update(self):
        self.lifetime -= 1
        
    def is_active(self):
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / 15))
        color = (255, 140, 0, alpha)
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(alpha)
        s.fill(ORANGE)
        screen.blit(s, (self.x, self.y))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("King of Python - Test Version")
        self.clock = pygame.time.Clock()
        
        # 平台
        self.platforms = [
            {'x': 0, 'y': HEIGHT - 50, 'width': WIDTH, 'height': 50},  # 地面
            {'x': 200, 'y': 400, 'width': 150, 'height': 20},
            {'x': 450, 'y': 350, 'width': 150, 'height': 20},
            {'x': 325, 'y': 250, 'width': 150, 'height': 20},
        ]
        
        # 玩家
        self.player1 = Player(100, 100, RED, {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'jump': pygame.K_w,
            'attack': pygame.K_SPACE
        })
        
        self.player2 = Player(650, 100, BLUE, {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'jump': pygame.K_UP,
            'attack': pygame.K_RETURN
        })
        
        # 泡泡
        self.bubbles = []
        self.bubble_spawn_timer = 0
        self.bubble_spawn_interval = 120  # 2秒
        
        # 攻击区域
        self.attack_zones = []
        
        # 游戏状态
        self.game_over = False
        self.winner = None
        
    def spawn_bubble(self):
        x = random.randint(100, WIDTH - 100)
        y = 0
        self.bubbles.append(Bubble(x, y))
        
    def check_bubble_collision(self, player):
        for bubble in self.bubbles[:]:
            if player.get_rect().colliderect(bubble.get_rect()):
                player.has_bubble = True
                self.bubbles.remove(bubble)
                
    def create_attack(self, player):
        if player.has_bubble:
            if player.facing_right:
                x = player.x + player.width
            else:
                x = player.x - 80
            y = player.y
            
            attack = AttackZone(x, y, 1 if player.facing_right else -1)
            self.attack_zones.append(attack)
            player.has_bubble = False
            
    def check_attack_hit(self, attack, attacker, defender):
        if attack.get_rect().colliderect(defender.get_rect()):
            knockback = KNOCKBACK_FORCE if attacker.facing_right else -KNOCKBACK_FORCE
            defender.take_damage(attack.damage, knockback)
            return True
        return False
        
    def check_game_over(self):
        # 检查HP
        if self.player1.hp <= 0:
            self.game_over = True
            self.winner = "Player 2 (Blue)"
        elif self.player2.hp <= 0:
            self.game_over = True
            self.winner = "Player 1 (Red)"
            
        # 检查掉出边界
        if self.player1.y > HEIGHT:
            self.game_over = True
            self.winner = "Player 2 (Blue)"
        elif self.player2.y > HEIGHT:
            self.game_over = True
            self.winner = "Player 1 (Red)"
            
    def draw_ui(self):
        font = pygame.font.Font(None, 36)
        
        # Player 1 HP
        pygame.draw.rect(self.screen, GRAY, (50, 30, 200, 30))
        hp_width = int(200 * (self.player1.hp / self.player1.max_hp))
        pygame.draw.rect(self.screen, RED, (50, 30, hp_width, 30))
        text = font.render(f"P1: {self.player1.hp}", True, WHITE)
        self.screen.blit(text, (60, 35))
        
        # Player 2 HP
        pygame.draw.rect(self.screen, GRAY, (550, 30, 200, 30))
        hp_width = int(200 * (self.player2.hp / self.player2.max_hp))
        pygame.draw.rect(self.screen, BLUE, (550, 30, hp_width, 30))
        text = font.render(f"P2: {self.player2.hp}", True, WHITE)
        self.screen.blit(text, (560, 35))
        
        # 控制提示
        small_font = pygame.font.Font(None, 24)
        p1_text = small_font.render("P1: WASD + Space", True, WHITE)
        p2_text = small_font.render("P2: Arrows + Enter", True, WHITE)
        self.screen.blit(p1_text, (50, 70))
        self.screen.blit(p2_text, (550, 70))
        
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        text = font.render(f"{self.winner} Wins!", True, GREEN)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(text, text_rect)
        
        small_font = pygame.font.Font(None, 36)
        restart_text = small_font.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
    def reset(self):
        self.__init__()
        
    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    if self.game_over and event.key == pygame.K_r:
                        self.reset()
                    
                    if not self.game_over:
                        if event.key == self.player1.controls['attack']:
                            self.create_attack(self.player1)
                        if event.key == self.player2.controls['attack']:
                            self.create_attack(self.player2)
            
            if not self.game_over:
                keys = pygame.key.get_pressed()
                
                # 更新玩家
                self.player1.update(keys, self.platforms)
                self.player2.update(keys, self.platforms)
                
                # 生成泡泡
                self.bubble_spawn_timer += 1
                if self.bubble_spawn_timer >= self.bubble_spawn_interval:
                    self.spawn_bubble()
                    self.bubble_spawn_timer = 0
                
                # 更新泡泡
                for bubble in self.bubbles[:]:
                    bubble.update()
                    if bubble.y > HEIGHT:
                        self.bubbles.remove(bubble)
                
                # 检查泡泡碰撞
                self.check_bubble_collision(self.player1)
                self.check_bubble_collision(self.player2)
                
                # 更新攻击区域
                for attack in self.attack_zones[:]:
                    attack.update()
                    if not attack.is_active():
                        self.attack_zones.remove(attack)
                
                # 检查攻击命中
                for attack in self.attack_zones[:]:
                    if attack in self.attack_zones:  # 确保还存在
                        # 判断是谁的攻击
                        p1_attack_area = pygame.Rect(self.player1.x - 100, self.player1.y - 50, 250, 150)
                        is_p1_attack = p1_attack_area.colliderect(attack.get_rect())
                        
                        if is_p1_attack:
                            if self.check_attack_hit(attack, self.player1, self.player2):
                                self.attack_zones.remove(attack)
                        else:
                            if self.check_attack_hit(attack, self.player2, self.player1):
                                self.attack_zones.remove(attack)
                
                # 检查游戏结束
                self.check_game_over()
            
            # 绘制
            self.screen.fill(BLACK)
            
            # 绘制平台
            for platform in self.platforms:
                pygame.draw.rect(self.screen, GREEN, 
                               (platform['x'], platform['y'], 
                                platform['width'], platform['height']))
            
            # 绘制泡泡
            for bubble in self.bubbles:
                bubble.draw(self.screen)
            
            # 绘制攻击区域
            for attack in self.attack_zones:
                attack.draw(self.screen)
            
            # 绘制玩家
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            
            # 绘制UI
            self.draw_ui()
            
            # 游戏结束画面
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
