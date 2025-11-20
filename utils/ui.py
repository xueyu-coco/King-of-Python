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
    
    # 技能说明 - SPACE 平台下方，等间距水平排列，整体居中
    space_bottom = HEIGHT - 100 + 38
    remaining_space = HEIGHT - space_bottom
    info_y = space_bottom + remaining_space // 2  # SPACE 底部到屏幕底部的中间位置
    
    skill_infos = [
        ("pow(): Attack 8HP", ORANGE),
        ("delete: Remove skill", RED),
        ("print: Shoot 2HP", YELLOW),
        ("super(): Giant 5s", (200, 100, 255)),
        ("Ctrl+C: Freeze 3s", CYAN),
        ("TypeError: Reverse 10s", DARK_RED)
    ]
    
    # 计算图标和文字的参数
    icon_radius = 6
    icon_text_gap = 8
    
    # 预渲染所有文字并计算每个技能项的宽度
    skill_items = []
    max_item_width = 0
    for text, color in skill_infos:
        skill_text = font_tiny.render(text, True, WHITE)
        item_width = icon_radius * 2 + icon_text_gap + skill_text.get_width()
        skill_items.append((skill_text, color, item_width))
        max_item_width = max(max_item_width, item_width)
    
    # 计算等间距排列：每个技能项占用相同宽度
    num_skills = len(skill_infos)
    total_width = WIDTH * 0.95  # 使用屏幕宽度的 95%
    item_spacing = total_width / num_skills  # 每个技能项占用的总宽度（包含间距）
    start_x = (WIDTH - total_width) / 2  # 起始 x 坐标，确保整体居中
    
    # 绘制每个技能说明
    for i, (skill_text, color, item_width) in enumerate(skill_items):
        # 计算当前技能项的中心位置
        item_center_x = start_x + item_spacing * i + item_spacing / 2
        
        # 计算图标和文字的起始位置（在分配的空间内居中）
        item_start_x = item_center_x - item_width / 2
        
        # 绘制彩色圆点图标
        icon_x = int(item_start_x + icon_radius)
        icon_y = int(info_y)
        pygame.draw.circle(screen, color, (icon_x, icon_y), icon_radius)
        
        # 绘制技能文字
        text_x = int(item_start_x + icon_radius * 2 + icon_text_gap)
        text_y = int(info_y)
        
        # 文字阴影（增强可读性）
        shadow_text = font_tiny.render(skill_infos[i][0], True, BLACK)
        shadow_rect = shadow_text.get_rect(midleft=(text_x + 1, text_y + 1))
        screen.blit(shadow_text, shadow_rect)
        
        # 主文字
        text_rect = skill_text.get_rect(midleft=(text_x, text_y))
        screen.blit(skill_text, text_rect)

