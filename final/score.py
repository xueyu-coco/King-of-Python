import pygame
import os
import math
import random
from settings import WIDTH, HEIGHT, KEY_SIDE, KEY_COLOR, KEY_SHADOW, ORANGE, YELLOW, BLACK, font_small, font_medium, CYAN, FPS


# Preload and clean monitor image at module import so animation can start instantly
MONITOR_SURF = None
try:
    # Prefer a no-background asset if present (user-supplied image)
    base_dir = os.path.dirname(__file__)
    preferred = os.path.join(base_dir, 'Computer_nobackground.png')
    fallback = os.path.join(base_dir, 'computer.png')
    img_path = preferred if os.path.exists(preferred) else fallback
    _raw = pygame.image.load(img_path)
    # If the loaded image already has per-pixel alpha, use it directly
    if _raw.get_flags() & pygame.SRCALPHA or _raw.get_alpha() is not None:
        _raw = _raw.convert_alpha()
        _mw, _mh = _raw.get_size()
        target_w, target_h = 520 - 20, 360 - 20
        scale = min(target_w / _mw, target_h / _mh)
        MONITOR_SURF = pygame.transform.smoothscale(_raw, (max(1, int(_mw * scale)), max(1, int(_mh * scale))))
    else:
        # Image has no alpha channel; remove near-white background into an alpha surface
        _raw = _raw.convert()
        _mw, _mh = _raw.get_size()
        _clean = pygame.Surface((_mw, _mh), pygame.SRCALPHA)
        try:
            _px = pygame.surfarray.pixels3d(_raw)
            # no alpha channel present; treat near-white pixels as transparent
            for _y in range(_mh):
                for _x in range(_mw):
                    r, g, b = _px[_x, _y]
                    if r > 245 and g > 245 and b > 245:
                        continue
                    _clean.set_at((_x, _y), (r, g, b, 255))
        except Exception:
            # fallback: blit raw to clean (no transparency cleanup)
            _clean.blit(_raw, (0, 0))
        target_w, target_h = 520 - 20, 360 - 20
        scale = min(target_w / _mw, target_h / _mh)
        MONITOR_SURF = pygame.transform.smoothscale(_clean, (max(1, int(_mw * scale)), max(1, int(_mh * scale))))
except Exception:
    MONITOR_SURF = None


# Preload crown image (pixel crown) for the final animation
CROWN_SURF = None
try:
    base_dir = os.path.dirname(__file__)
    crown_path = os.path.join(base_dir, 'Crown.png')
    if os.path.exists(crown_path):
        _c = pygame.image.load(crown_path)
        # prefer alpha-preserving surface
        if _c.get_flags() & pygame.SRCALPHA or _c.get_alpha() is not None:
            CROWN_SURF = _c.convert_alpha()
        else:
            CROWN_SURF = _c.convert()
except Exception:
    CROWN_SURF = None


# Preload optional final background image to use inside the decorative frame
FINAL_BG_SURF = None
try:
    base_dir = os.path.dirname(__file__)
    final_bg_path = os.path.join(base_dir, 'Final_background.png')
    if os.path.exists(final_bg_path):
        _bg = pygame.image.load(final_bg_path)
        # prefer alpha-preserving surface when available
        if _bg.get_flags() & pygame.SRCALPHA or _bg.get_alpha() is not None:
            FINAL_BG_SURF = _bg.convert_alpha()
        else:
            FINAL_BG_SURF = _bg.convert()
except Exception:
    FINAL_BG_SURF = None


# Preload an updated full-screen final background (preferred)
FINAL_BG_UPDATE_SURF = None
try:
    base_dir = os.path.dirname(__file__)
    final_bg_update_path = os.path.join(base_dir, 'Final_background_update.png')
    if os.path.exists(final_bg_update_path):
        _bg2 = pygame.image.load(final_bg_update_path)
        if _bg2.get_flags() & pygame.SRCALPHA or _bg2.get_alpha() is not None:
            FINAL_BG_UPDATE_SURF = _bg2.convert_alpha()
        else:
            FINAL_BG_UPDATE_SURF = _bg2.convert()
except Exception:
    FINAL_BG_UPDATE_SURF = None

# Pre-scale the updated final background to cover the screen (cover semantics)
# We allow separate overall scaling and width-compression so the image can be
# slightly larger while being narrower horizontally (user-requested).
FINAL_BG_UPDATE_SCALED = None
try:
    if FINAL_BG_UPDATE_SURF is not None:
        bw, bh = FINAL_BG_UPDATE_SURF.get_size()
        # Slightly enlarge overall, but compress horizontal length more
        OVERALL_BG_SCALE = 1.02  # slightly smaller overall scale
        BG_WIDTH_COMPRESS = 0.82  # reduce horizontal compression (less squashed)
        BG_HEIGHT_COMPRESS = 0.82  # slightly stronger vertical compression to reduce height a bit
        base_scale = max(WIDTH / bw, HEIGHT / bh) * OVERALL_BG_SCALE
        new_w = max(1, int(bw * base_scale * BG_WIDTH_COMPRESS))
        new_h = max(1, int(bh * base_scale * BG_HEIGHT_COMPRESS))
        # Prevent vertical cropping: if the compressed height still exceeds the
        # screen height, scale down so new_h == HEIGHT (no top/bottom cutoff).
        if new_h > HEIGHT:
            scale_down = HEIGHT / float(new_h)
            new_h = HEIGHT
            new_w = max(1, int(new_w * scale_down))
        try:
            FINAL_BG_UPDATE_SCALED = pygame.transform.smoothscale(FINAL_BG_UPDATE_SURF, (new_w, new_h))
        except Exception:
            FINAL_BG_UPDATE_SCALED = pygame.transform.scale(FINAL_BG_UPDATE_SURF, (new_w, new_h))
    else:
        FINAL_BG_UPDATE_SCALED = None
except Exception:
    FINAL_BG_UPDATE_SCALED = None


def play_score_animation(screen, winner, loser, winner_avatar=None):
    # --- UI装饰函数 ---
    def draw_hearts(surface, x, y, count, spacing=28, size=18, color=(255, 200, 255)):
        for i in range(count):
            cx = x + i * spacing
            left = (cx - size//4, y)
            right = (cx + size//4, y)
            # top point not used explicitly; circle + polygon form the heart
            pygame.draw.circle(surface, color, left, size//3)
            pygame.draw.circle(surface, color, right, size//3)
            points = [(cx - size//2, y), (cx + size//2, y), (cx, y + size//2)]
            pygame.draw.polygon(surface, color, points)

    def draw_score_ui(surface):
        # If a pre-scaled full-screen updated background is provided, use it and skip the purple frame.
        if FINAL_BG_UPDATE_SCALED is not None:
            try:
                bw, bh = FINAL_BG_UPDATE_SCALED.get_size()
                # small offset to nudge the image slightly right
                FINAL_BG_OFFSET_X = 20
                FINAL_BG_OFFSET_Y = 12
                bx = (WIDTH - bw) // 2 + FINAL_BG_OFFSET_X + (globals().get('SCENE_SHIFT_X') if 'SCENE_SHIFT_X' in globals() else 0)
                by = (HEIGHT - bh) // 2 + FINAL_BG_OFFSET_Y
                # Clamp vertical position so the image never extends off-screen
                if by < 0:
                    by = 0
                if by + bh > HEIGHT:
                    by = HEIGHT - bh
                # Clear to solid black first so no gameplay remnants show outside the background
                try:
                    surface.fill(BLACK)
                except Exception:
                    surface.fill((0, 0, 0))
                # draw the pre-scaled background (centered)
                surface.blit(FINAL_BG_UPDATE_SCALED, (bx, by))
            except Exception:
                # fallback to the purple frame if blit fails
                surface.fill((180, 120, 220))
                inner_rect = pygame.Rect(40, 40, WIDTH - 80, HEIGHT - 120)
                pygame.draw.rect(surface, BLACK, inner_rect)
            return

        # 紫色外框和黑色内框 (fallback behavior)
        surface.fill((180, 120, 220))
        inner_rect = pygame.Rect(40, 40, WIDTH - 80, HEIGHT - 120)
        # If a final background image is provided, draw it into the inner rect.
        # Keep aspect ratio and center it. Otherwise fallback to a flat black background.
        if FINAL_BG_SURF is not None:
            try:
                bw, bh = FINAL_BG_SURF.get_size()
                # compute scale to fit inner rect while preserving aspect
                scale = min((inner_rect.width) / bw, (inner_rect.height) / bh)
                new_w = max(1, int(bw * scale))
                new_h = max(1, int(bh * scale))
                try:
                    bg_s = pygame.transform.smoothscale(FINAL_BG_SURF, (new_w, new_h))
                except Exception:
                    bg_s = pygame.transform.scale(FINAL_BG_SURF, (new_w, new_h))
                bx = inner_rect.left + (inner_rect.width - new_w) // 2
                by = inner_rect.top + (inner_rect.height - new_h) // 2
                # draw a subtle black fill behind the image for safety
                pygame.draw.rect(surface, BLACK, inner_rect)
                surface.blit(bg_s, (bx, by))
            except Exception:
                pygame.draw.rect(surface, BLACK, inner_rect)
        else:
            pygame.draw.rect(surface, BLACK, inner_rect)
        # 顶部 hearts
        draw_hearts(surface, inner_rect.left + 80, inner_rect.top + 20, 10, spacing=40, size=20, color=(240, 200, 255))
        # 底部说明文字（上移一些避免与标题重叠）
        sub = font_small.render('Press SPACE to continue', True, (220, 220, 240))
        surface.blit(sub, (inner_rect.centerx - sub.get_width()//2, inner_rect.bottom - 80))
    """Play a short ending animation: winner walks to a computer, sits, and wears a crown.

    Args:
        screen: pygame display surface
        winner: Player object who won
        loser: Player object who lost (may be used for camera framing)
        winner_avatar: Optional surface to show as avatar during the sequence
    """
    clock = pygame.time.Clock()

    # (No special background) use normal BG_COLOR (import from settings if needed at module level)

    # Setup simple scene positions (computer centered on screen)
    # enlarge the monitor so the pixel-art image is more prominent
    SCENE_SHIFT_X = -40
    # Nudge the losing player's position (and its avatar) further left so it sits closer to the monitor
    LOSER_NUDGE = -48
    comp_w = 520
    comp_h = 360
    # center monitor in the middle of the screen (apply scene shift)
    comp_x = WIDTH // 2 + SCENE_SHIFT_X
    comp_y = HEIGHT // 2 + 80  # slightly lower than exact center so characters sit comfortably
    monitor_rect = pygame.Rect(comp_x - comp_w // 2, comp_y - comp_h // 2 - 20, comp_w, comp_h)
    chair_x = comp_x - 40
    chair_y = monitor_rect.bottom + 6

    # Pre-render VICTORY text and rect so we can position the winner above it
    vt = font_medium.render("VICTORY", True, ORANGE)
    vt_rect = vt.get_rect(center=(monitor_rect.centerx, monitor_rect.centery))
    VT_FEET_GAP = 8  # pixels gap between top of victory text and winner's feet
    WINNER_SCALE = 1.4  # how much larger the winner should appear in the final scene

    # prefer the preloaded pixel crown if available; keep legacy fallback
    crown = CROWN_SURF

    # Determine target x for winner to walk to (center of computer)
    target_x = comp_x - winner.width // 2
    walking = True
    sit_timer = 0
    # show crown from the start of the animation
    crown_timer = FPS * 6
    crown_allowed = True
    # Prepare jump animation params
    jump_phase = 0.0
    jump_speed = 0.18
    jump_height = 40

    # tears for loser
    tears = []

    # Freeze both players movement for the animation
    winner.vel_x = 0
    winner.vel_y = 0
    loser.vel_x = 0
    loser.vel_y = 0

    # Save gameplay-related state and clear effects so final animation isn't affected
    _saved_winner_state = {}
    _saved_loser_state = {}
    try:
        for p, storage in ((winner, _saved_winner_state), (loser, _saved_loser_state)):
            storage['is_super'] = getattr(p, 'is_super', False)
            storage['super_timer'] = getattr(p, 'super_timer', 0)
            storage['super_collision_cooldown'] = getattr(p, 'super_collision_cooldown', 0)
            storage['is_frozen'] = getattr(p, 'is_frozen', False)
            storage['freeze_timer'] = getattr(p, 'freeze_timer', 0)
            storage['is_reversed'] = getattr(p, 'is_reversed', False)
            storage['reverse_timer'] = getattr(p, 'reverse_timer', 0)
            storage['skill'] = getattr(p, 'skill', None)
            storage['is_attacking'] = getattr(p, 'is_attacking', False)
            storage['attack_frame'] = getattr(p, 'attack_frame', 0)
            storage['attack_cooldown'] = getattr(p, 'attack_cooldown', 0)
            storage['knockback_x'] = getattr(p, 'knockback_x', 0)
            storage['vel_x'] = getattr(p, 'vel_x', 0)
            storage['vel_y'] = getattr(p, 'vel_y', 0)
            storage['on_ground'] = getattr(p, 'on_ground', False)

            # clear active effects
            p.is_super = False
            p.super_timer = 0
            p.super_collision_cooldown = 0
            p.is_frozen = False
            p.freeze_timer = 0
            p.is_reversed = False
            p.reverse_timer = 0
            p.skill = None
            p.is_attacking = False
            p.attack_frame = 0
            p.attack_cooldown = 0
            p.knockback_x = 0
            p.vel_x = 0
            p.vel_y = 0
            p.on_ground = True
    except Exception:
        # if anything goes wrong, fall back to not crashing the animation
        _saved_winner_state = {}
        _saved_loser_state = {}

    # Place loser beside the monitor image (prefer right side if there's space)
    # default spacing from monitor edge (smaller so avatar sits closer)
    side_spacing = 8  # reduced spacing to bring loser closer horizontally
    # preferred to the right of the monitor
    right_x = monitor_rect.right + side_spacing
    left_x = monitor_rect.left - side_spacing - loser.width
    # choose the side that fits within the screen; prefer right if room
    if right_x + loser.width + 16 < WIDTH:
        loser_target_x = right_x
    else:
        loser_target_x = max(8, left_x)
    # nudge loser slightly up and left to sit visually closer to the monitor
    loser.x = int(loser_target_x) - 8 + LOSER_NUDGE
    loser.y = monitor_rect.bottom - loser.height + 10

    # Use a module-preloaded monitor surface for instant start
    monitor_s = MONITOR_SURF

    # Walk loop: move winner toward target_x
    for frame in range(FPS * 6):  # up to 6 seconds
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return

        # move winner toward target
        if walking:
            if abs(winner.x - target_x) > 4:
                step = 3 if winner.x < target_x else -3
                winner.x += step
                winner.facing_right = True if step > 0 else False
            else:
                walking = False
                sit_timer = FPS * 1  # 1 second to sit

        elif sit_timer > 0:
            # small sitting animation: lower y a bit
            winner.y += (chair_y - winner.y) * 0.2
            sit_timer -= 1
            if sit_timer <= 0:
                # start crown timer immediately and allow crown to appear as soon as jump starts
                crown_timer = FPS * 2  # 2 seconds as safety, but we'll also show crown when jumping begins

        elif crown_timer > 0:
            crown_timer -= 1


        # 先画UI装饰
        draw_score_ui(screen)

        # 再画原有胜利场景（电脑、椅子、角色等）
        # draw computer (base + monitor)
        # Prefer using a pixel-art monitor image if available in final/computer.png
        # draw monitor: use preloaded image if available
        if monitor_s is not None:
            screen.blit(monitor_s, (monitor_rect.centerx - monitor_s.get_width()//2, monitor_rect.centery - monitor_s.get_height()//2))
        else:
            base_h = 12
            base_rect = pygame.Rect(monitor_rect.left, monitor_rect.bottom + 6, comp_w, base_h)
            pygame.draw.rect(screen, KEY_SIDE, base_rect)
            pygame.draw.rect(screen, KEY_COLOR, monitor_rect)
            pygame.draw.rect(screen, KEY_SHADOW, monitor_rect, 3)

            # draw chair (decorative) under the monitor area only when drawing the fallback monitor
            pygame.draw.rect(screen, KEY_SIDE, (chair_x, chair_y, 50, 10))
            pygame.draw.rect(screen, KEY_COLOR, (chair_x, chair_y - 30, 50, 30))

        # draw VICTORY text at the same position each frame (position unchanged)
        screen.blit(vt, vt_rect)

    # (chair is drawn with the fallback monitor only)

        # draw loser beside the computer (prefer right side when space allows)
        side_spacing = 8
        right_x = monitor_rect.right + side_spacing
        left_x = monitor_rect.left - side_spacing - loser.width
        if right_x + loser.width + 16 < WIDTH:
            loser_target_x = right_x
        else:
            loser_target_x = max(8, left_x)
        # apply the same visual nudge as initial placement (left and up)
        loser.x = int(loser_target_x) - 8 + LOSER_NUDGE
        loser.y = monitor_rect.bottom - loser.height + 10
        # Prevent duplicate avatars: temporarily hide loser's avatar while drawing base sprite
        try:
            _saved_avatar = getattr(loser, 'avatar', None)
            _saved_cached = getattr(loser, '_cached_avatar', None)
            try:
                loser.avatar = None
            except Exception:
                pass
            try:
                loser._cached_avatar = None
            except Exception:
                pass

            # draw the loser's body (without avatar)
            loser.draw(screen)

            # draw a single avatar manually (shifted left to sit closer to monitor)
            avatar_surf = _saved_avatar or _saved_cached
            if avatar_surf:
                try:
                    aw, ah = avatar_surf.get_size()
                    max_aw = int(loser.width * 0.5)
                    max_ah = int(loser.height * 0.5)
                    scale = min(max_aw / aw if aw else 1, max_ah / ah if ah else 1, 1)
                    new_w = max(1, int(aw * scale))
                    new_h = max(1, int(ah * scale))
                    try:
                        av = pygame.transform.smoothscale(avatar_surf, (new_w, new_h))
                    except Exception:
                        av = pygame.transform.scale(avatar_surf, (new_w, new_h))
                    # Center avatar within the loser's frame (same logic as winner)
                    ax = int(loser.x + (loser.width - av.get_width()) / 2)
                    ay = int(loser.y + (loser.height - av.get_height()) / 2)
                    screen.blit(av, (ax, ay))
                except Exception:
                    pass
        finally:
            # restore avatar fields
            try:
                loser.avatar = _saved_avatar
            except Exception:
                pass
            try:
                loser._cached_avatar = _saved_cached
            except Exception:
                pass

        # draw winner (on top of monitor, jumping)
        if not walking:
            jump_phase += jump_speed
            offset = -int(abs(math.sin(jump_phase)) * jump_height)
            # place the winner so their feet sit above the top of the VICTORY text
            base_y = vt_rect.top - winner.height - VT_FEET_GAP
            winner.y = base_y + offset
            # allow crown once the winner has actually reached the base_y (i.e. above VICTORY)
            if not crown_allowed:
                try:
                    if abs(winner.y - base_y) <= 2:
                        crown_allowed = True
                except Exception:
                    crown_allowed = True
        winner.x = int(winner.x)
        # draw enlarged winner for the final animation (do not modify Player permanently)
        try:
            scale = WINNER_SCALE
            expanded_w = int(winner.width * scale)
            expanded_h = int(winner.height * scale)
            # Align expanded image such that the feet align with original bottom (winner.y + winner.height)
            draw_x = int(winner.x + winner.width / 2 - expanded_w / 2)
            draw_y = int(winner.y + winner.height - expanded_h)

            if getattr(winner, 'use_image', False) and getattr(winner, 'current_image', None):
                img = winner.current_image
                if not winner.facing_right:
                    try:
                        img = pygame.transform.flip(img, True, False)
                    except Exception:
                        pass
                try:
                    big = pygame.transform.smoothscale(img, (expanded_w, expanded_h))
                except Exception:
                    big = pygame.transform.scale(img, (expanded_w, expanded_h))
                screen.blit(big, (draw_x, draw_y))
                # draw avatar inside the enlarged sprite if available
                avatar_surf = None
                if getattr(winner, 'avatar', None):
                    avatar_surf = winner.avatar
                elif getattr(winner, '_cached_avatar', None):
                    avatar_surf = winner._cached_avatar

                if avatar_surf:
                    try:
                        aw, ah = avatar_surf.get_size()
                        max_aw = int(expanded_w * 0.5)
                        max_ah = int(expanded_h * 0.5)
                        scale = min(max_aw / aw if aw else 1, max_ah / ah if ah else 1, 1)
                        new_w = max(1, int(aw * scale))
                        new_h = max(1, int(ah * scale))
                        try:
                            av = pygame.transform.smoothscale(avatar_surf, (new_w, new_h))
                        except Exception:
                            av = pygame.transform.scale(avatar_surf, (new_w, new_h))
                        ax = draw_x + (expanded_w - av.get_width()) // 2
                        ay = draw_y + (expanded_h - av.get_height()) // 2
                        screen.blit(av, (ax, ay))
                    except Exception:
                        pass
            else:
                # fallback: draw a larger rect
                pygame.draw.rect(screen, winner.color, (draw_x, draw_y, expanded_w, expanded_h))
                # draw avatar inside enlarged rect if available
                avatar_surf = getattr(winner, 'avatar', None) or getattr(winner, '_cached_avatar', None)
                if avatar_surf:
                    try:
                        aw, ah = avatar_surf.get_size()
                        max_aw = int(expanded_w * 0.5)
                        max_ah = int(expanded_h * 0.5)
                        scale = min(max_aw / aw if aw else 1, max_ah / ah if ah else 1, 1)
                        new_w = max(1, int(aw * scale))
                        new_h = max(1, int(ah * scale))
                        try:
                            av = pygame.transform.smoothscale(avatar_surf, (new_w, new_h))
                        except Exception:
                            av = pygame.transform.scale(avatar_surf, (new_w, new_h))
                        ax = draw_x + (expanded_w - av.get_width()) // 2
                        ay = draw_y + (expanded_h - av.get_height()) // 2
                        screen.blit(av, (ax, ay))
                    except Exception:
                        pass
        except Exception:
            # On any error, fall back to the normal draw call
            try:
                winner.draw(screen)
            except Exception:
                pass

        # no avatar above the winner in the final animation (keep screen clean)
        # show crown when timer active OR when the winner has started the jump animation
        # only draw crown after the winner has moved into position above VICTORY
        if crown_allowed and (crown_timer > 0 or jump_phase > 0 or (not walking and sit_timer <= 0)):
            # position crown relative to the enlarged winner drawing
            cx = int(winner.x + winner.width//2)
            cy = int(winner.y - 22)
            if crown is not None:
                try:
                    cw, ch = crown.get_size()
                    # crown should scale roughly with the enlarged winner width
                    desired_w = int(winner.width * WINNER_SCALE * 0.9)
                    scale_h = int(ch * (desired_w / cw)) if cw else ch
                    crown_s = pygame.transform.smoothscale(crown, (max(1, desired_w), max(1, scale_h)))
                    screen.blit(crown_s, (cx - crown_s.get_width()//2, cy - crown_s.get_height()//2))
                except Exception:
                    # fallback to simple polygon if crown blit fails
                    points = [(cx - 18, cy + 12), (cx - 12, cy - 6), (cx - 4, cy + 8), (cx + 4, cy - 6), (cx + 12, cy + 12)]
                    pygame.draw.polygon(screen, ORANGE, points)
                    pygame.draw.polygon(screen, YELLOW, points, 2)
            else:
                points = [(cx - 18, cy + 12), (cx - 12, cy - 6), (cx - 4, cy + 8), (cx + 4, cy - 6), (cx + 12, cy + 12)]
                pygame.draw.polygon(screen, ORANGE, points)
                pygame.draw.polygon(screen, YELLOW, points, 2)

    # top-left caption removed per UX request

        # draw tears for loser
        if random.random() < 0.12:
            eye_x = int(loser.x + loser.width * 0.5)
            eye_y = int(loser.y + 16)
            tears.append({'x': eye_x + random.randint(-6, 6), 'y': eye_y, 'vy': 2 + random.random()*2})

        for t in tears[:]:
            pygame.draw.circle(screen, CYAN, (int(t['x']), int(t['y'])), 3)
            t['y'] += t['vy']
            t['vy'] += 0.12
            if t['y'] > HEIGHT:
                tears.remove(t)

        pygame.display.flip()

        # early exit when crown animation done (mark finished instead of returning immediately)
        finished = False
        if not walking and sit_timer <= 0 and crown_timer <= 0:
            finished = True
            break

    # If the animation reached the finished state, keep rendering the final scene
    # until the player presses SPACE. This allows the animation to loop indefinitely
    # and only continue when the user confirms.
    if 'finished' in locals() and finished:
        waiting = True
        while waiting:
            clock.tick(FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    waiting = False
            # Advance jump animation so the winner keeps bouncing while waiting
            try:
                if not walking:
                    jump_phase += jump_speed
                    offset = -int(abs(math.sin(jump_phase)) * jump_height)
                    base_y = vt_rect.top - winner.height - VT_FEET_GAP
                    winner.y = base_y + offset
                    # allow crown once the winner is roughly at base_y
                    if not crown_allowed:
                        try:
                            if abs(winner.y - base_y) <= 2:
                                crown_allowed = True
                        except Exception:
                            crown_allowed = True
                winner.x = int(winner.x)
            except Exception:
                pass

            # redraw final UI and scene each frame
            draw_score_ui(screen)

            # draw monitor (use preloaded image if available)
            if monitor_s is not None:
                try:
                    screen.blit(monitor_s, (monitor_rect.centerx - monitor_s.get_width()//2, monitor_rect.centery - monitor_s.get_height()//2))
                except Exception:
                    pass
            else:
                try:
                    base_h = 12
                    base_rect = pygame.Rect(monitor_rect.left, monitor_rect.bottom + 6, comp_w, base_h)
                    pygame.draw.rect(screen, KEY_SIDE, base_rect)
                    pygame.draw.rect(screen, KEY_COLOR, monitor_rect)
                    pygame.draw.rect(screen, KEY_SHADOW, monitor_rect, 3)
                    pygame.draw.rect(screen, KEY_SIDE, (chair_x, chair_y, 50, 10))
                    pygame.draw.rect(screen, KEY_COLOR, (chair_x, chair_y - 30, 50, 30))
                except Exception:
                    pass

            # draw VICTORY text
            try:
                screen.blit(vt, vt_rect)
            except Exception:
                pass

            # draw loser (reuse the same safe avatar logic)
            try:
                side_spacing = 8
                right_x = monitor_rect.right + side_spacing
                left_x = monitor_rect.left - side_spacing - loser.width
                if right_x + loser.width + 16 < WIDTH:
                    loser_target_x = right_x
                else:
                    loser_target_x = max(8, left_x)
                loser.x = int(loser_target_x) - 8 + LOSER_NUDGE
                loser.y = monitor_rect.bottom - loser.height + 10

                _saved_avatar = getattr(loser, 'avatar', None)
                _saved_cached = getattr(loser, '_cached_avatar', None)
                try:
                    loser.avatar = None
                except Exception:
                    pass
                try:
                    loser._cached_avatar = None
                except Exception:
                    pass

                loser.draw(screen)

                avatar_surf = _saved_avatar or _saved_cached
                if avatar_surf:
                    try:
                        aw, ah = avatar_surf.get_size()
                        max_aw = int(loser.width * 0.5)
                        max_ah = int(loser.height * 0.5)
                        scale = min(max_aw / aw if aw else 1, max_ah / ah if ah else 1, 1)
                        new_w = max(1, int(aw * scale))
                        new_h = max(1, int(ah * scale))
                        try:
                            av = pygame.transform.smoothscale(avatar_surf, (new_w, new_h))
                        except Exception:
                            av = pygame.transform.scale(avatar_surf, (new_w, new_h))
                        ax = int(loser.x + (loser.width - av.get_width()) / 2)
                        ay = int(loser.y + (loser.height - av.get_height()) / 2)
                        screen.blit(av, (ax, ay))
                    except Exception:
                        pass
                try:
                    loser.avatar = _saved_avatar
                except Exception:
                    pass
                try:
                    loser._cached_avatar = _saved_cached
                except Exception:
                    pass
            except Exception:
                pass

            # draw enlarged winner and avatar
            try:
                scale = WINNER_SCALE
                expanded_w = int(winner.width * scale)
                expanded_h = int(winner.height * scale)
                draw_x = int(winner.x + winner.width / 2 - expanded_w / 2)
                draw_y = int(winner.y + winner.height - expanded_h)

                if getattr(winner, 'use_image', False) and getattr(winner, 'current_image', None):
                    img = winner.current_image
                    if not winner.facing_right:
                        try:
                            img = pygame.transform.flip(img, True, False)
                        except Exception:
                            pass
                    try:
                        big = pygame.transform.smoothscale(img, (expanded_w, expanded_h))
                    except Exception:
                        big = pygame.transform.scale(img, (expanded_w, expanded_h))
                    screen.blit(big, (draw_x, draw_y))
                    avatar_surf = None
                    if getattr(winner, 'avatar', None):
                        avatar_surf = winner.avatar
                    elif getattr(winner, '_cached_avatar', None):
                        avatar_surf = winner._cached_avatar

                    if avatar_surf:
                        try:
                            aw, ah = avatar_surf.get_size()
                            max_aw = int(expanded_w * 0.5)
                            max_ah = int(expanded_h * 0.5)
                            scale = min(max_aw / aw if aw else 1, max_ah / ah if ah else 1, 1)
                            new_w = max(1, int(aw * scale))
                            new_h = max(1, int(ah * scale))
                            try:
                                av = pygame.transform.smoothscale(avatar_surf, (new_w, new_h))
                            except Exception:
                                av = pygame.transform.scale(avatar_surf, (new_w, new_h))
                            ax = draw_x + (expanded_w - av.get_width()) // 2
                            ay = draw_y + (expanded_h - av.get_height()) // 2
                            screen.blit(av, (ax, ay))
                        except Exception:
                            pass
                else:
                    pygame.draw.rect(screen, winner.color, (draw_x, draw_y, expanded_w, expanded_h))
                    avatar_surf = getattr(winner, 'avatar', None) or getattr(winner, '_cached_avatar', None)
                    if avatar_surf:
                        try:
                            aw, ah = avatar_surf.get_size()
                            max_aw = int(expanded_w * 0.5)
                            max_ah = int(expanded_h * 0.5)
                            scale = min(max_aw / aw if aw else 1, max_ah / ah if ah else 1, 1)
                            new_w = max(1, int(aw * scale))
                            new_h = max(1, int(ah * scale))
                            try:
                                av = pygame.transform.smoothscale(avatar_surf, (new_w, new_h))
                            except Exception:
                                av = pygame.transform.scale(avatar_surf, (new_w, new_h))
                            ax = draw_x + (expanded_w - av.get_width()) // 2
                            ay = draw_y + (expanded_h - av.get_height()) // 2
                            screen.blit(av, (ax, ay))
                        except Exception:
                            pass
            except Exception:
                try:
                    winner.draw(screen)
                except Exception:
                    pass

            # draw crown
            try:
                if crown is not None:
                    cw, ch = crown.get_size()
                    desired_w = int(winner.width * WINNER_SCALE * 0.9)
                    scale_h = int(ch * (desired_w / cw)) if cw else ch
                    crown_s = pygame.transform.smoothscale(crown, (max(1, desired_w), max(1, scale_h)))
                    cx = int(winner.x + winner.width//2)
                    cy = int(winner.y - 22)
                    screen.blit(crown_s, (cx - crown_s.get_width()//2, cy - crown_s.get_height()//2))
            except Exception:
                pass

            # tears update
            try:
                if random.random() < 0.12:
                    eye_x = int(loser.x + loser.width * 0.5)
                    eye_y = int(loser.y + 16)
                    tears.append({'x': eye_x + random.randint(-6, 6), 'y': eye_y, 'vy': 2 + random.random()*2})
            except Exception:
                pass

            for t in tears[:]:
                try:
                    pygame.draw.circle(screen, CYAN, (int(t['x']), int(t['y'])), 3)
                    t['y'] += t['vy']
                    t['vy'] += 0.12
                    if t['y'] > HEIGHT:
                        tears.remove(t)
                except Exception:
                    pass

            pygame.display.flip()

    # Restore saved gameplay state so players resume normal behavior after the animation
    try:
        for p, storage in ((winner, _saved_winner_state), (loser, _saved_loser_state)):
            if not storage:
                continue
            try:
                p.is_super = storage.get('is_super', False)
                p.super_timer = storage.get('super_timer', 0)
                p.super_collision_cooldown = storage.get('super_collision_cooldown', 0)
                p.is_frozen = storage.get('is_frozen', False)
                p.freeze_timer = storage.get('freeze_timer', 0)
                p.is_reversed = storage.get('is_reversed', False)
                p.reverse_timer = storage.get('reverse_timer', 0)
                p.skill = storage.get('skill', None)
                p.is_attacking = storage.get('is_attacking', False)
                p.attack_frame = storage.get('attack_frame', 0)
                p.attack_cooldown = storage.get('attack_cooldown', 0)
                p.knockback_x = storage.get('knockback_x', 0)
                p.vel_x = storage.get('vel_x', 0)
                p.vel_y = storage.get('vel_y', 0)
                p.on_ground = storage.get('on_ground', False)
            except Exception:
                # ignore restore errors
                pass
    except Exception:
        pass
