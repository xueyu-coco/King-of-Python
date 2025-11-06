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

