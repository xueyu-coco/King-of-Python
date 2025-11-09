from entities.platform import KeyPlatform
from settings import *

def create_keyboard_platforms():
    """创建键盘主题的平台布局"""
    platforms = []
    
    # SPACE键 - 最底部的主平台（超长）
    platforms.append(KeyPlatform(50, HEIGHT - 80, 700, 30, "SPACE"))
    
    # QWER 行 - 中层平台
    platforms.append(KeyPlatform(100, 350, 80, 25, "Q"))
    platforms.append(KeyPlatform(220, 350, 80, 25, "W"))
    platforms.append(KeyPlatform(340, 350, 80, 25, "E"))
    platforms.append(KeyPlatform(580, 350, 80, 25, "R"))
    
    # ASD 行 - 较低层
    platforms.append(KeyPlatform(150, 420, 80, 25, "A"))
    platforms.append(KeyPlatform(420, 420, 80, 25, "S"))
    platforms.append(KeyPlatform(530, 420, 80, 25, "D"))
    
    # Shift键 - 动态升降平台（左侧）
    platforms.append(KeyPlatform(50, 280, 120, 25, "Shift", is_dynamic=True))
    
    # Tab键 - 高层平台
    platforms.append(KeyPlatform(620, 250, 100, 25, "Tab"))
    
    return platforms

