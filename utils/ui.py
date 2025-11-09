import pygame
from settings import *

def draw_ui(screen, player1, player2, p1_avatar=None, p2_avatar=None):
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
    
    # 技能说明
    info_y = HEIGHT - 120
    pow_info = font_tiny.render("pow(): Attack 8HP", True, ORANGE)
    delete_info = font_tiny.render("delete: Remove enemy skill", True, RED)
    print_info = font_tiny.render("print: Shoot 'Attack!' 2HP", True, YELLOW)
    ctrlc_info = font_tiny.render("Ctrl+C: Freeze 3s", True, CYAN)
    type_info = font_tiny.render("TypeError: Reverse controls 10s", True, DARK_RED)
    
    screen.blit(pow_info, (WIDTH//2 - 130, info_y))
    screen.blit(delete_info, (WIDTH//2 - 130, info_y + 20))
    screen.blit(print_info, (WIDTH//2 - 130, info_y + 40))
    screen.blit(ctrlc_info, (WIDTH//2 - 130, info_y + 60))
    screen.blit(type_info, (WIDTH//2 - 130, info_y + 80))

