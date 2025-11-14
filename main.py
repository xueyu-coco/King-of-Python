import pygame
import sys
import os
import random
import time
from settings import *
from entities.player import Player
from entities.bubble import Bubble
from entities.projectile import Projectile
from entities.platform import KeyPlatform
from final.score import play_score_animation
from Backround import backround_1 as background

try:
    HERE = os.path.dirname(__file__)
    REPO_ROOT = os.path.abspath(HERE)
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    # try to import the batch two-face capture helper if available
    # Import face capture helpers only when not explicitly disabled via env.
    if os.environ.get('DISABLE_FACE') != '1':
        from face_detection.face_login_demo import capture_two_and_make_sprites, capture_and_make_sprite
    else:
        capture_two_and_make_sprites = None
        capture_and_make_sprite = None
except Exception:
    # fall back to single-capture function if batch isn't available
    try:
        from face_detection.face_login_demo import capture_and_make_sprite
        capture_two_and_make_sprites = None
    except Exception:
        capture_and_make_sprite = None
        capture_two_and_make_sprites = None



def check_player_collision(player1, player2):
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
    # 血条右对齐，扣血时从左边消失
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
    # SPACE 平台位置：(75, HEIGHT - 100, 1050, 38)
    space_bottom = HEIGHT - 100 + 38
    # 计算SPACE平台底部到屏幕底部的距离，将技能说明放在中间偏上
    remaining_space = HEIGHT - space_bottom
    info_y = space_bottom + remaining_space // 3  # 在剩余空间的1/3位置
    
    # 技能说明列表
    skill_infos = [
        ("pow(): Attack 8HP", ORANGE),
        ("delete: Remove skill", RED),
        ("print: Shoot 2HP", YELLOW),
        ("Ctrl+C: Freeze 3s", CYAN),
        ("TypeError: Reverse 10s", DARK_RED)
    ]
    
    # 计算每个技能说明的实际宽度
    icon_radius = 6
    icon_text_gap = 10  # 图标和文字之间的间距
    skill_item_spacing = 20  # 技能之间的间距
    
    # 预渲染所有文字，计算总宽度
    rendered_texts = []
    total_content_width = 0
    for text, color in skill_infos:
        skill_text = font_tiny.render(text, True, WHITE)
        text_width = skill_text.get_width()
        item_width = icon_radius * 2 + icon_text_gap + text_width
        rendered_texts.append((skill_text, text_width))
        total_content_width += item_width
    
    # 加上技能之间的间距
    total_content_width += skill_item_spacing * (len(skill_infos) - 1)
    
    # 计算起始x坐标，使整体居中
    start_x = (WIDTH - total_content_width) / 2
    
    # 绘制每个技能说明
    current_x = start_x
    for i, ((text, color), (skill_text, text_width)) in enumerate(zip(skill_infos, rendered_texts)):
        # 绘制彩色圆点作为图标
        icon_x = int(current_x + icon_radius)
        icon_y = int(info_y + 8)
        pygame.draw.circle(screen, color, (icon_x, icon_y), icon_radius)
        
        # 绘制技能文字
        text_x = int(current_x + icon_radius * 2 + icon_text_gap)
        text_y = int(info_y + 8)
        
        # 添加文字阴影增强可读性
        shadow_text = font_tiny.render(text, True, BLACK)
        shadow_rect = shadow_text.get_rect(midleft=(text_x + 1, text_y + 1))
        screen.blit(shadow_text, shadow_rect)
        
        # 绘制主文字
        text_rect = skill_text.get_rect(midleft=(text_x, text_y))
        screen.blit(skill_text, text_rect)
        
        # 移动到下一个技能的位置
        current_x += icon_radius * 2 + icon_text_gap + text_width + skill_item_spacing

def create_keyboard_platforms():
    """创建键盘主题的平台布局"""
    platforms = []
    
    # SPACE键 - 最底部的主平台（超长）
    platforms.append(KeyPlatform(75, HEIGHT - 100, 1050, 38, "SPACE"))
    
    # QWER 行 - 中层平台（调整位置，增加横向和纵向间距）
    platforms.append(KeyPlatform(280, 480, 100, 32, "Q"))
    platforms.append(KeyPlatform(400, 410, 100, 32, "W"))
    platforms.append(KeyPlatform(580, 485, 100, 32, "E"))
    platforms.append(KeyPlatform(920, 465, 100, 32, "R"))
    
    # ASD 行 - 较低层（调整位置，增加间距）
    platforms.append(KeyPlatform(150, 580, 100, 32, "A"))
    platforms.append(KeyPlatform(680, 570, 100, 32, "S"))
    platforms.append(KeyPlatform(850, 590, 100, 32, "D"))
    
    # Shift键 - 可断裂平台（左侧，位置调整避免正好被Q接住）
    platforms.append(KeyPlatform(75, 360, 100, 32, "Shift", is_dynamic=True, is_breakable=True))
    
    # Tab键 - 高层平台
    platforms.append(KeyPlatform(950, 320, 125, 32, "Tab"))
    
    return platforms

def main():
    clock = pygame.time.Clock()
    start = True
    local_p1 = None
    local_p2 = None
    global screen, WIDTH, HEIGHT
    # if display was quit by external code (e.g. face capture), re-init it
    if not pygame.get_init() or not pygame.display.get_init() or pygame.display.get_surface() is None:
        pygame.init()
        # recreate the screen surface from settings
        try:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("King of Python - The Great Keyboard")
        except Exception:
            # if settings not available, ignore; errors will surface later
            pass
    
    while start:
        screen.fill(BG_COLOR)
        # DEBUG: sanity checks for font before rendering
        try:
            print('DEBUG font_large type:', type(font_large), 'hasattr render:', hasattr(font_large, 'render'))
            print('DEBUG text length:', len('King of Python'))
        except Exception:
            pass
        # Use the project's PURPLE for title/subtitle so UI matches the background tint
        title = font_large.render('King of Python', True, PURPLE)
        sub = font_small.render('Press SPACE to capture faces, S to skip and start', True, PURPLE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))
        pygame.display.flip()
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                start = False
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.VIDEORESIZE:
                # recreate main display and update background target
                try:
                    WIDTH, HEIGHT = ev.w, ev.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    background.set_surface(screen)
                except Exception:
                    pass
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE and (capture_two_and_make_sprites is not None or capture_and_make_sprite is not None):
                    # Prefer a single-shot two-face capture if available
                    if capture_two_and_make_sprites is not None:
                        try:
                            p1, p2 = capture_two_and_make_sprites('Face1', 'Face2')
                        except KeyboardInterrupt:
                            # user aborted capture (Ctrl+C) - skip avatar capture
                            p1 = None
                            p2 = None
                        except Exception:
                            # fallback to sequential captures if batch capture fails
                            try:
                                p1 = capture_and_make_sprite('Face1') if capture_and_make_sprite else None
                            except Exception:
                                p1 = None
                            time.sleep(1.0)
                            try:
                                p2 = capture_and_make_sprite('Face2') if capture_and_make_sprite else None
                            except Exception:
                                p2 = None
                    else:
                        try:
                            p1 = capture_and_make_sprite('Face1')
                        except Exception:
                            p1 = None
                        time.sleep(1.0)
                        try:
                            p2 = capture_and_make_sprite('Face2')
                        except Exception:
                            p2 = None

                    local_p1 = load_avatar_surface(p1)
                    local_p2 = load_avatar_surface(p2)
                    start = False
                if ev.key == pygame.K_s:
                    start = False
    
    # 创建键盘平台
    platforms = create_keyboard_platforms()

    # 将背景渲染目标设为主屏幕（背景模块现在是导入安全的）
    try:
        background.set_surface(screen)
    except Exception:
        # 如果背景模块不可用或 set_surface 失败，不影响主流程
        pass
    
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
    
    player1 = Player(200, 300, BLUE, player1_controls, facing_right=True, avatar=local_p1)
    player2 = Player(550, 300, RED, player2_controls, facing_right=False, avatar=local_p2)
    
    bubbles = []
    projectiles = []
    bubble_timer = 0
    
    running = True
    game_over = False
    winner = None
    score_shown = False
    
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
                
                if not game_over:
                    if event.key == player1.controls['attack']:
                        skill_used = player1.use_skill()
                        if skill_used:
                            last_p1_skill = skill_used
                            if skill_used == 'print':
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
            
            # 更新动态平台
            for platform in platforms:
                platform.update(players=[player1, player2])
            
            # 更新玩家（只使用未断裂的平台）
            active_platforms = [p for p in platforms if not p.is_broken]
            player1.update(keys, active_platforms)
            player2.update(keys, active_platforms)
            
            check_player_collision(player1, player2)
            
            # 检测攻击
            if player1.is_attacking and player1.attack_frame == 5 and not player1.is_frozen:
                if last_p1_skill == 'pow' and check_attack_hit(player1, player2):
                    knockback_dir = 1 if player1.facing_right else -1
                    player2.take_damage(8, knockback_dir)
                    last_p1_skill = None
                elif last_p1_skill == 'delete' and check_attack_hit(player1, player2):
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
                # 泡泡生成概率：pow 25%, delete 15%, print 25%, ctrlc 20%, typeerror 15%
                rand = random.random()
                if rand < 0.25:
                    btype = 'pow'
                elif rand < 0.40:
                    btype = 'delete'
                elif rand < 0.65:
                    btype = 'print'
                elif rand < 0.85:
                    btype = 'ctrlc'
                else:
                    btype = 'typeerror'
                bubbles.append(Bubble(x, -50, btype))
                bubble_timer = 0
            
            # 更新泡泡
            for bubble in bubbles[:]:
                bubble.update()
                if not bubble.active:
                    bubbles.remove(bubble)
                else:
                    if bubble.check_collision(player1):
                        if bubble.type in ['pow', 'delete', 'print'] and player1.skill is None:
                            player1.skill = bubble.type
                        elif bubble.type == 'ctrlc':
                            player1.freeze()
                            player1.take_damage(3, 0)  # 捡到ctrl+c扣3点血
                        elif bubble.type == 'typeerror':
                            player1.reverse_controls()
                            player1.take_damage(3, 0)  # 捡到typeerror扣3点血
                        bubbles.remove(bubble)
                        continue

                    if bubble.check_collision(player2):
                        if bubble.type in ['pow', 'delete', 'print'] and player2.skill is None:
                            player2.skill = bubble.type
                        elif bubble.type == 'ctrlc':
                            player2.freeze()
                            player2.take_damage(3, 0)  # 捡到ctrl+c扣3点血
                        elif bubble.type == 'typeerror':
                            player2.reverse_controls()
                            player2.take_damage(3, 0)  # 捡到typeerror扣3点血
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

        # 背景更新与绘制（来自 Backround.backround_1）
        try:
            background.update(pygame.time.get_ticks())
            background.draw(screen)
        except Exception:
            # if background fails, ignore so main loop continues
            pass
        
        # 绘制所有键盘平台
        for platform in platforms:
            platform.draw(screen)
        
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
            if not score_shown:
                # determine winner and loser objects
                if winner == "PLAYER 1":
                    play_score_animation(screen, player1, player2, winner_avatar=local_p1)
                else:
                    play_score_animation(screen, player2, player1, winner_avatar=local_p2)
                score_shown = True
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
