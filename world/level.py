"""关卡和平台布局配置"""
from entities.platform import KeyPlatform
from settings import HEIGHT


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

