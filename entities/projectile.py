import pygame
from settings import *

class Projectile:
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner
        self.vel_x = PROJECTILE_SPEED * direction
        self.active = True
        self.damage = 2
        self.text = "Attack!"
        
    def update(self):
        self.x += self.vel_x
        if self.x < -50 or self.x > WIDTH + 50:
            self.active = False
    
    def draw(self, screen):
        text = font_small.render(self.text, True, YELLOW)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        
        glow_text = font_small.render(self.text, True, (255, 255, 200))
        glow_rect = glow_text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(glow_text, (glow_rect.x + 2, glow_rect.y + 2))
        screen.blit(text, text_rect)
    
    def check_collision(self, player):
        if player == self.owner:
            return False
        
        proj_rect = pygame.Rect(self.x - 30, self.y - 15, 60, 30)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        return proj_rect.colliderect(player_rect)