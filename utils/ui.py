"""UI绘制相关函数"""
import pygame
from settings import *


def draw_ui(screen, player1, player2, p1_avatar=None, p2_avatar=None):
    """绘制游戏UI：血条、头像、技能说明"""
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
    p1_text = font_tiny.render(name1, True, player1.color)
    if p1_text.get_width() > hp_bar_width:
        small_font = pygame.font.Font(FONT_PATH, 18)
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
    
    # 玩家2血条（从右到左填充，扣血时从左边减少，保持右对齐）
    p2_x = WIDTH - 50 - hp_bar_width
    pygame.draw.rect(screen, GRAY, (p2_x, hp_bar_y, hp_bar_width, hp_bar_height))
    hp2_width = int((player2.hp / player2.max_hp) * hp_bar_width)
    hp2_start_x = p2_x + (hp_bar_width - hp2_width)
    pygame.draw.rect(screen, player2.color, (hp2_start_x, hp_bar_y, hp2_width, hp_bar_height))
    pygame.draw.rect(screen, BLACK, (p2_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
    
    name2 = "PLAYER 2"
    p2_text = font_tiny.render(name2, True, player2.color)
    if p2_text.get_width() > hp_bar_width:
        small_font = pygame.font.Font(FONT_PATH, 18)
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
    
    # 技能说明 - 移到 SPACE 平台下方，水平排列，居中显示
    space_bottom = HEIGHT - 100 + 38
    remaining_space = HEIGHT - space_bottom
    info_y = space_bottom + remaining_space // 3
    
    skill_infos = [
        ("pow(): Attack 8HP", ORANGE),
        ("delete: Remove skill", RED),
        ("print: Shoot 2HP", YELLOW),
        ("super(): Giant 5s", (200, 100, 255)),
        ("Ctrl+C: Freeze 3s", CYAN),
        ("TypeError: Reverse 10s", DARK_RED)
    ]
    
    # 计算每个技能说明的实际宽度
    icon_radius = 6
    icon_text_gap = 10
    skill_item_spacing = 20
    
    # 预渲染所有文字，计算总宽度
    rendered_texts = []
    total_content_width = 0
    for text, color in skill_infos:
        skill_text = font_tiny.render(text, True, WHITE)
        text_width = skill_text.get_width()
        item_width = icon_radius * 2 + icon_text_gap + text_width
        rendered_texts.append((skill_text, text_width))
        total_content_width += item_width
    
    total_content_width += skill_item_spacing * (len(skill_infos) - 1)
    start_x = (WIDTH - total_content_width) / 2
    
    # 绘制每个技能说明
    current_x = start_x
    for i, ((text, color), (skill_text, text_width)) in enumerate(zip(skill_infos, rendered_texts)):
        # 绘制彩色圆点
        icon_x = int(current_x + icon_radius)
        icon_y = int(info_y + 8)
        pygame.draw.circle(screen, color, (icon_x, icon_y), icon_radius)
        
        # 绘制技能文字
        text_x = int(current_x + icon_radius * 2 + icon_text_gap)
        text_y = int(info_y + 8)
        
        # 文字阴影
        shadow_text = font_tiny.render(text, True, BLACK)
        shadow_rect = shadow_text.get_rect(midleft=(text_x + 1, text_y + 1))
        screen.blit(shadow_text, shadow_rect)
        
        # 主文字
        text_rect = skill_text.get_rect(midleft=(text_x, text_y))
        screen.blit(skill_text, text_rect)
        
        current_x += icon_radius * 2 + icon_text_gap + text_width + skill_item_spacing

