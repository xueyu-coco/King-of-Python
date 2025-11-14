"""玩家头像加载相关功能"""
import pygame
import os
import sys
import time

# 初始化路径和导入人脸识别模块
try:
    HERE = os.path.dirname(__file__)
    REPO_ROOT = os.path.abspath(os.path.join(HERE, '..'))
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    
    # 导入人脸捕获辅助函数（除非环境变量禁用）
    if os.environ.get('DISABLE_FACE') != '1':
        from face_detection.face_login_demo import capture_two_and_make_sprites, capture_and_make_sprite
    else:
        capture_two_and_make_sprites = None
        capture_and_make_sprite = None
except Exception:
    # 回退到单人脸捕获函数
    try:
        from face_detection.face_login_demo import capture_and_make_sprite
        capture_two_and_make_sprites = None
    except Exception:
        capture_and_make_sprite = None
        capture_two_and_make_sprites = None


def load_avatar_surface(path, max_display=80):
    """
    加载头像图片并缩放到合适大小
    
    Args:
        path: 图片文件路径
        max_display: 最大显示尺寸（像素）
    
    Returns:
        pygame.Surface 或 None
    """
    try:
        surf = pygame.image.load(path).convert_alpha()
    except Exception:
        return None
    w, h = surf.get_size()
    if max(w, h) > max_display:
        scale = max_display / max(w, h)
        surf = pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))
    return surf


def capture_player_avatars():
    """
    捕获两个玩家的头像
    
    Returns:
        tuple: (p1_path, p2_path) 两个玩家头像文件路径，失败时为 None
    """
    # 优先使用批量双人脸捕获
    if capture_two_and_make_sprites is not None:
        try:
            p1, p2 = capture_two_and_make_sprites('Face1', 'Face2')
            return p1, p2
        except KeyboardInterrupt:
            # 用户中止捕获（Ctrl+C）
            return None, None
        except Exception:
            # 批量捕获失败，回退到顺序捕获
            pass
    
    # 回退到顺序捕获
    if capture_and_make_sprite is not None:
        try:
            p1 = capture_and_make_sprite('Face1')
        except Exception:
            p1 = None
        
        time.sleep(1.0)
        
        try:
            p2 = capture_and_make_sprite('Face2')
        except Exception:
            p2 = None
        
        return p1, p2
    
    return None, None
