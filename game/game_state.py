"""游戏状态管理类"""
import pygame
import random
from entities.bubble import Bubble
from entities.projectile import Projectile
from settings import BUBBLE_SPAWN_TIME


class GameState:
    """管理游戏核心状态和逻辑"""
    
    def __init__(self, player1, player2, platforms):
        self.player1 = player1
        self.player2 = player2
        self.platforms = platforms
        self.bubbles = []
        self.projectiles = []
        self.bubble_timer = 0
        self.game_over = False
        self.winner = None
        self.score_shown = False
        self.last_p1_skill = None
        self.last_p2_skill = None
    
    def reset(self):
        """重置游戏状态"""
        self.bubbles.clear()
        self.projectiles.clear()
        self.bubble_timer = 0
        self.game_over = False
        self.winner = None
        self.score_shown = False
        self.last_p1_skill = None
        self.last_p2_skill = None
    
    def spawn_bubble(self, WIDTH):
        """生成技能泡泡"""
        self.bubble_timer += 1
        if self.bubble_timer >= BUBBLE_SPAWN_TIME:
            x = random.randint(100, WIDTH - 100)
            # 泡泡生成概率：pow 20%, delete 12%, print 20%, super 10%, ctrlc 18%, typeerror 20%
            rand = random.random()
            if rand < 0.20:
                btype = 'pow'
            elif rand < 0.32:
                btype = 'delete'
            elif rand < 0.52:
                btype = 'print'
            elif rand < 0.62:
                btype = 'super'
            elif rand < 0.80:
                btype = 'ctrlc'
            else:
                btype = 'typeerror'
            self.bubbles.append(Bubble(x, -50, btype))
            self.bubble_timer = 0
    
    def update_bubbles(self):
        """更新泡泡状态和碰撞检测"""
        for bubble in self.bubbles[:]:
            bubble.update()
            if not bubble.active:
                self.bubbles.remove(bubble)
            else:
                # 检测玩家1碰撞
                if bubble.check_collision(self.player1):
                    if bubble.type in ['pow', 'delete', 'print'] and self.player1.skill is None:
                        self.player1.skill = bubble.type
                    elif bubble.type == 'super' and not self.player1.is_super:
                        self.player1.activate_super()
                    elif bubble.type == 'ctrlc':
                        self.player1.freeze()
                        self.player1.take_damage(3, 0)
                    elif bubble.type == 'typeerror':
                        self.player1.reverse_controls()
                        self.player1.take_damage(3, 0)
                    self.bubbles.remove(bubble)
                    continue
                
                # 检测玩家2碰撞
                if bubble.check_collision(self.player2):
                    if bubble.type in ['pow', 'delete', 'print'] and self.player2.skill is None:
                        self.player2.skill = bubble.type
                    elif bubble.type == 'super' and not self.player2.is_super:
                        self.player2.activate_super()
                    elif bubble.type == 'ctrlc':
                        self.player2.freeze()
                        self.player2.take_damage(3, 0)
                    elif bubble.type == 'typeerror':
                        self.player2.reverse_controls()
                        self.player2.take_damage(3, 0)
                    self.bubbles.remove(bubble)
    
    def update_projectiles(self):
        """更新飞行道具和碰撞检测"""
        for proj in self.projectiles[:]:
            proj.update()
            if not proj.active:
                self.projectiles.remove(proj)
            else:
                if proj.check_collision(self.player1) and proj.owner != self.player1:
                    knockback = 10 if proj.direction > 0 else -10
                    self.player1.take_damage(proj.damage, knockback)
                    self.projectiles.remove(proj)
                elif proj.check_collision(self.player2) and proj.owner != self.player2:
                    knockback = 10 if proj.direction > 0 else -10
                    self.player2.take_damage(proj.damage, knockback)
                    self.projectiles.remove(proj)
    
    def check_game_over(self):
        """检查游戏是否结束"""
        if self.player1.hp <= 0:
            self.game_over = True
            self.winner = "PLAYER 2"
        elif self.player2.hp <= 0:
            self.game_over = True
            self.winner = "PLAYER 1"
    
    def draw_entities(self, screen):
        """绘制所有游戏实体"""
        # 绘制平台
        for platform in self.platforms:
            platform.draw(screen)
        
        # 绘制泡泡
        for bubble in self.bubbles:
            bubble.draw(screen)
        
        # 绘制飞行道具
        for proj in self.projectiles:
            proj.draw(screen)
        
        # 绘制玩家
        self.player1.draw(screen)
        self.player2.draw(screen)
