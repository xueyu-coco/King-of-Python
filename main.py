"""King of Python - 主游戏入口"""
import pygame
import sys
from settings import *
from entities.player import Player
from entities.projectile import Projectile
from final.score import play_score_animation
from Backround import backround_1 as background
from game.collision import check_player_collision, check_attack_hit
from game.game_state import GameState
from game.avatar import capture_player_avatars, load_avatar_surface
from utils.ui import draw_ui
from world.level import create_keyboard_platforms



def show_start_screen(screen):
    """显示游戏开始界面，处理头像捕获"""
    global WIDTH, HEIGHT
    local_p1 = None
    local_p2 = None
    
    start = True
    while start:
        screen.fill(BG_COLOR)
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
                # 窗口大小调整时重新创建显示
                try:
                    WIDTH, HEIGHT = ev.w, ev.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    background.set_surface(screen)
                except Exception:
                    pass
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    # 捕获头像
                    p1_path, p2_path = capture_player_avatars()
                    local_p1 = load_avatar_surface(p1_path)
                    local_p2 = load_avatar_surface(p2_path)
                    start = False
                if ev.key == pygame.K_s:
                    start = False
    
    return local_p1, local_p2


def handle_player_attacks(game_state):
    """处理玩家攻击逻辑"""
    player1 = game_state.player1
    player2 = game_state.player2
    
    # 玩家1攻击
    if player1.is_attacking and player1.attack_frame == 5 and not player1.is_frozen:
        if game_state.last_p1_skill == 'pow' and check_attack_hit(player1, player2):
            knockback_dir = 1 if player1.facing_right else -1
            player2.take_damage(8, knockback_dir)
            game_state.last_p1_skill = None
        elif game_state.last_p1_skill == 'delete' and check_attack_hit(player1, player2):
            player2.skill = None
            game_state.last_p1_skill = None
    
    # 玩家2攻击
    if player2.is_attacking and player2.attack_frame == 5 and not player2.is_frozen:
        if game_state.last_p2_skill == 'pow' and check_attack_hit(player2, player1):
            knockback_dir = 1 if player2.facing_right else -1
            player1.take_damage(8, knockback_dir)
            game_state.last_p2_skill = None
        elif game_state.last_p2_skill == 'delete' and check_attack_hit(player2, player1):
            player1.skill = None
            game_state.last_p2_skill = None


def handle_skill_usage(event, game_state):
    """处理玩家技能使用"""
    player1 = game_state.player1
    player2 = game_state.player2
    
    if event.key == player1.controls['attack']:
        skill_used = player1.use_skill()
        if skill_used:
            game_state.last_p1_skill = skill_used
            if skill_used == 'print':
                proj_x = player1.x + player1.width if player1.facing_right else player1.x
                proj_y = player1.y + player1.height // 2
                direction = 1 if player1.facing_right else -1
                game_state.projectiles.append(Projectile(proj_x, proj_y, direction, player1))
    
    if event.key == player2.controls['attack']:
        skill_used = player2.use_skill()
        if skill_used:
            game_state.last_p2_skill = skill_used
            if skill_used == 'print':
                proj_x = player2.x + player2.width if player2.facing_right else player2.x
                proj_y = player2.y + player2.height // 2
                direction = 1 if player2.facing_right else -1
                game_state.projectiles.append(Projectile(proj_x, proj_y, direction, player2))


def draw_game_over_screen(screen, winner):
    """绘制游戏结束画面"""
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



def main():
    """主游戏循环"""
    clock = pygame.time.Clock()
    global screen, WIDTH, HEIGHT
    
    # 如果显示被外部代码关闭（如人脸捕获），重新初始化
    if not pygame.get_init() or not pygame.display.get_init() or pygame.display.get_surface() is None:
        pygame.init()
        try:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("King of Python - The Great Keyboard")
        except Exception:
            pass
    
    # 显示开始画面并捕获头像
    local_p1, local_p2 = show_start_screen(screen)
    
    # 创建键盘平台
    platforms = create_keyboard_platforms()

    # 设置背景渲染目标
    try:
        background.set_surface(screen)
    except Exception:
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
    
    # 初始化游戏状态
    game_state = GameState(player1, player2, platforms)
    
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_state.game_over and event.key == pygame.K_SPACE:
                    return
                
                # 处理技能使用
                if not game_state.game_over:
                    handle_skill_usage(event, game_state)
        
        # 游戏逻辑更新
        if not game_state.game_over:
            keys = pygame.key.get_pressed()
            
            # 更新动态平台
            for platform in platforms:
                platform.update(players=[player1, player2])
            
            # 更新玩家（只使用未断裂的平台）
            active_platforms = [p for p in platforms if not p.is_broken]
            player1.update(keys, active_platforms)
            player2.update(keys, active_platforms)
            
            # 检测玩家碰撞
            check_player_collision(player1, player2)
            
            # 检测攻击
            handle_player_attacks(game_state)
            
            # 更新飞行道具
            game_state.update_projectiles()
            
            # 生成和更新泡泡
            game_state.spawn_bubble(WIDTH)
            game_state.update_bubbles()
            
            # 检查游戏结束
            game_state.check_game_over()
        
        # 绘制
        screen.fill(BG_COLOR)

        # 背景更新与绘制
        try:
            background.update(pygame.time.get_ticks())
            background.draw(screen)
        except Exception:
            pass
        
        # 绘制所有游戏实体
        game_state.draw_entities(screen)
        
        # 绘制玩家
        player1.draw(screen)
        player2.draw(screen)
        
        # 绘制UI
        draw_ui(screen, player1, player2, p1_avatar=local_p1, p2_avatar=local_p2)
        
        # 游戏结束画面
        if game_state.game_over:
            if not game_state.score_shown:
                # 播放得分动画
                if game_state.winner == "PLAYER 1":
                    play_score_animation(screen, player1, player2, winner_avatar=local_p1)
                else:
                    play_score_animation(screen, player2, player1, winner_avatar=local_p2)
                game_state.score_shown = True
            
            draw_game_over_screen(screen, game_state.winner)

        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    while True:
        main()
