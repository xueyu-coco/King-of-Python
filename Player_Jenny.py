class Player:
    def __init__(self, x, y, color, controls, facing_right=True):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80
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
        self.attack_power = 3
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
        
        # 攻击：只有拾取到 pow 泡泡后才能攻击（攻击会消耗 pow）
        if keys[self.controls['attack']] and self.attack_cooldown <= 0 and self.has_pow_bubble:
            self.is_attacking = True
            self.attack_cooldown = ATTACK_COOLDOWN
            # powered attack
            self.attack_power = 8
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
    
    def draw(self, screen, avatar=None):
        # 绘制角色方块
        if self.is_attacking and self.attack_frame % 4 < 2:
            # 攻击时闪烁效果
            color = (min(255, self.color[0] + 50), 
                    min(255, self.color[1] + 50), 
                    min(255, self.color[2] + 50))
        else:
            color = self.color
        
        # 如果提供了 avatar（合成的 frame + photo），则将其缩放到角色方块的大小并替代方块绘制
        if avatar:
            try:
                sprite = pygame.transform.smoothscale(avatar, (self.width, self.height))
                screen.blit(sprite, (int(self.x), int(self.y)))
            except Exception:
                # 回退到原始方块绘制（无边框）
                pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))
        else:
            # 仅绘制填充色方块（不再绘制黑色边框或眼睛）
            pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))
        
        # 眼睛与边框已移除 — 现在只显示头像或填充色方块
        
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