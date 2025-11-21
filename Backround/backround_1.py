import pygame
import random
import math
import os
import glob

# NOTE: This module used to initialize Pygame and create a display at import time.
# That caused import-time side effects. Make the module import-safe by deferring
# pygame.init() and display.set_mode() until `init(..., create_display=True)` or
# until an external caller calls `set_surface(surface)`.

# Window size defaults (can be overridden by init or set_surface)
cw, ch = 1200, 800
screen = None  # rendering target surface (set by init(create_display=True) or set_surface)
bg_surface = None  # internal transparent surface we draw the streams onto

# Global alpha scale for the streams (0.0 - 1.0). Lower to make streams more transparent.
# Slightly reduced so purple code characters are a bit more transparent while keeping
# brightness and other behavior unchanged.
ALPHA_SCALE = 0.55  # reduced from 0.65 -> 0.55 to lower purple opacity a bit

# Color definitions: boosted vivid palette — purples are brighter and more saturated
PALETTE = [
    (200,  80, 255),  # shift slightly toward blue (less red)
    (200,  90, 230),  # magenta -> cooler magenta with more blue
    (255, 120, 180),  # brighter pink (keep)
    (100, 220, 200),  # pastel aqua (keep)
    (120, 240, 180),  # pastel mint (keep)
    (220, 160, 255),  # vivid lavender (slightly cooler)
]
BLACK = (0, 0, 0)

# Font tint colors (primary and head) to give characters a cute purple look
# Increase purple brightness/saturation for character tinting
FONT_TINT = (200, 40, 255)    # lean slightly blue (reduce red component)
FONT_HEAD_TINT = (200, 200, 255)  # head tint shifted slightly blue

# Character array - includes digits and uppercase letters similar to the reference image
char_arr = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Stream settings
max_char_count = 80
char_streams = []
font_size = 20
stream_speed_min = 2
stream_speed_max = 8

# Per-character scale parameters (tweak to reduce jitter)
SCALE_MIN = 0.78
SCALE_MAX = 1.40

# Compute number of columns
columns = cw // font_size
module_font = None
module_is_pixel_font = False

class CharStream:
    def __init__(self, column):
        self.column = column
        self.x = column * font_size
        self.chars = []
        self.speed = random.uniform(stream_speed_min, stream_speed_max)
        self.stream_length = random.randint(8, 25)
        self.head_char_index = 0
        self.last_char_time = 0
        self.char_interval = 100  # 毫秒
    # static scaling: no per-frame scale tracking
        # assign a base pastel color for this stream
        self.base_color = random.choice(PALETTE)
        self.generate_initial_chars()
    
    def generate_initial_chars(self):
        # Create initial characters starting above the screen
        for i in range(self.stream_length):
            char = {
                'value': random.choice(char_arr),
                'y': -i * font_size,  # 从屏幕外开始
                'bright': False,
                # per-character static scale (1.0 = normal)
                'scale': random.uniform(SCALE_MIN, SCALE_MAX),
            }
            # no special bright head character
            self.chars.append(char)
    
    def update(self, current_time):
        # Update character positions
        for char in self.chars:
            # keep original vertical behavior
            char['y'] += self.speed

        # static scales: scales assigned at creation and not animated per-frame
        
        # Remove characters that go off-screen and add new ones
        if self.chars and self.chars[0]['y'] > ch:
            self.chars.pop(0)
            new_char = {
                'value': random.choice(char_arr),
                'y': self.chars[-1]['y'] - font_size if self.chars else -font_size,
                'bright': False,
                'scale': random.uniform(SCALE_MIN, SCALE_MAX),
            }
            self.chars.append(new_char)
        
        # no blinking bright character logic
    
    def draw(self, screen, font):
        global module_is_pixel_font
        for i, char in enumerate(self.chars):
            # Character color gradient - head is brightest, tail fades
            if char['bright']:
                # head uses a tint towards FONT_HEAD_TINT for a cute purple head
                color = FONT_HEAD_TINT
                # brighter head alpha
                alpha = 245
            else:
                # Compute brightness based on position in the stream; top characters are brighter
                raw = 1.0 - (i / self.stream_length)
                brightness = max(0.15, 0.95 * raw)
                # base color contribution
                base_col = (
                    int(self.base_color[0] * brightness),
                    int(self.base_color[1] * brightness),
                    int(self.base_color[2] * brightness)
                )
                # blend base color with FONT_TINT to bias characters toward purple
                blend = 0.75
                color = (
                    int(base_col[0] * (1 - blend) + FONT_TINT[0] * blend),
                    int(base_col[1] * (1 - blend) + FONT_TINT[1] * blend),
                    int(base_col[2] * (1 - blend) + FONT_TINT[2] * blend),
                )
                # overall alpha scaled by brightness (make slightly stronger)
                alpha = int(245 * brightness)

            # 绘制字符（使用 alpha 调低亮度）
            if 0 <= char['y'] <= ch:
                # render base text surface
                # For pixel fonts, disable antialiasing to keep a crisp/blocky look;
                # for non-pixel fonts prefer antialiasing for smoother glyphs.
                try:
                    antialias = False if module_is_pixel_font else True
                except Exception:
                    antialias = True
                text_surf = font.render(char['value'], antialias, color).convert_alpha()
                # apply alpha and scale
                scale = char.get('scale', 1.0)
                sw = max(1, int(text_surf.get_width() * scale))
                sh = max(1, int(text_surf.get_height() * scale))

                # prepare scaled surfaces for base, outline and glow
                try:
                    # prefer nearest-neighbor scaling for pixel fonts to keep blocky look
                    if module_is_pixel_font:
                        base_scaled = pygame.transform.scale(text_surf, (sw, sh)) if (sw != text_surf.get_width() or sh != text_surf.get_height()) else text_surf
                    else:
                        base_scaled = pygame.transform.smoothscale(text_surf, (sw, sh)) if (sw != text_surf.get_width() or sh != text_surf.get_height()) else text_surf
                except Exception:
                    base_scaled = pygame.transform.scale(text_surf, (sw, sh)) if (sw != text_surf.get_width() or sh != text_surf.get_height()) else text_surf

                # Scale alpha by global ALPHA_SCALE and compute blit positions
                try:
                    base_alpha = max(0, min(255, int(alpha * ALPHA_SCALE)))
                except Exception:
                    base_alpha = alpha
                blit_x = int(self.x + (font_size - sw) / 2)
                blit_y = int(char['y'] - (sh - font_size))

                # draw the base character (no outline, no glow)
                # To make the background characters appear bolder (thicker),
                # draw the main glyph once at full alpha and then draw a few
                # slightly-offset copies at reduced alpha to simulate a bold
                # stroke without changing the font face.
                base_scaled.set_alpha(base_alpha)
                screen.blit(base_scaled, (blit_x, blit_y))

                # extra offset blits to thicken the glyph (reduce their alpha)
                extra_alpha = max(0, min(255, int(base_alpha * 0.55)))
                base_scaled.set_alpha(extra_alpha)
                for ox, oy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    try:
                        screen.blit(base_scaled, (blit_x + ox, blit_y + oy))
                    except Exception:
                        # ignore any blit errors (safe fallback)
                        pass

def create_streams():
    """Create initial digit rain streams"""
    global char_streams
    char_streams = []

    # Randomly select columns to create streams
    available_columns = list(range(columns))
    random.shuffle(available_columns)

    num_streams = min(max_char_count, len(available_columns))
    for i in range(num_streams):
        col = available_columns[i]
        stream = CharStream(col)
        char_streams.append(stream)

def handle_resize(event):
    """Handle a resize event or (w,h) tuple.

    This will update internal cw/ch/columns and recreate streams, but it will
    NOT create a new display surface. The caller (usually main) is
    responsible for creating the display surface and calling `set_surface`.
    """
    global cw, ch, columns
    if hasattr(event, 'w') and hasattr(event, 'h'):
        cw, ch = event.w, event.h
    elif isinstance(event, (tuple, list)) and len(event) == 2:
        cw, ch = int(event[0]), int(event[1])
    else:
        return
    columns = cw // font_size
    # recreate internal bg surface to match new size (if created)
    global bg_surface
    try:
        if screen is not None:
            bg_surface = pygame.Surface((cw, ch), pygame.SRCALPHA)
    except Exception:
        bg_surface = None
    create_streams()


def init(width=None, height=None, create_display=False, caption="Matrix Digital Rain"):
    """Initialize module settings.

    If create_display is True this will also call pygame.init() and create
    a display surface which will be used as the target for draw().
    Otherwise the module will be import-safe and require set_surface(surface)
    or the caller to pass a surface to draw().
    """
    global cw, ch, columns, screen
    if width is not None:
        cw = int(width)
    if height is not None:
        ch = int(height)
    columns = cw // font_size
    if create_display:
        pygame.init()
        screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
        pygame.display.set_caption(caption)
    create_streams()


def set_surface(surface):
    """Set an external surface as the rendering target (safe for embedding).

    Passing the main display surface here lets the background draw into the
    game's main screen without the module creating its own window.
    """
    global screen, cw, ch, columns
    screen = surface
    try:
        w, h = surface.get_size()
        cw, ch = int(w), int(h)
        columns = cw // font_size
    except Exception:
        # surface may not be a pygame Surface; ignore size update if so
        pass
    # create an internal transparent surface that we'll blit onto the target
    global bg_surface
    try:
        bg_surface = pygame.Surface((cw, ch), pygame.SRCALPHA)
    except Exception:
        bg_surface = None
    create_streams()

def main():
    global char_streams
    # Standalone runner: initializes pygame and creates a display
    global module_font, module_is_pixel_font
    pygame.init()
    screen_local = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
    pygame.display.set_caption("Matrix Digital Rain")

    # create font
    # Prefer the project's bundled pixel font for the standalone runner as
    # well so that standalone visuals match the embedded background when
    # the pixel font is available. Fall back to courier if not found.
    font = None
    try:
        fonts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fonts'))
        candidates = glob.glob(os.path.join(fonts_dir, 'ark-pixel-12px-proportional-*.otf'))
        chosen = None
        if candidates:
            for p in candidates:
                if 'latin' in os.path.basename(p).lower():
                    chosen = p
                    break
            if chosen is None:
                chosen = candidates[0]
            font = pygame.font.Font(chosen, font_size)
            module_font = font
            module_is_pixel_font = True
    except Exception:
        font = None

    if font is None:
        try:
            font = pygame.font.SysFont('couriernew', font_size, bold=True)
            module_font = font
            module_is_pixel_font = False
        except Exception:
            font = pygame.font.Font(None, font_size)
            module_font = font
            module_is_pixel_font = False

    # set our surface so draw() can use it
    set_surface(screen_local)

    clock = pygame.time.Clock()
    running = True

    # fill screen once to initialize
    screen_local.fill(BLACK)

    while running:
        current_time = pygame.time.get_ticks()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # caller is responsible for recreating the display; set_surface
                # will be called from the caller if necessary. Here we update
                # internal sizes and streams only.
                handle_resize(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen each frame (no motion trail)
        screen_local.fill(BLACK)

        # Update streams and draw them onto an internal transparent surface,
        # then blit that surface onto the screen so the background has a
        # transparent base (only characters are opaque)
        for stream in char_streams:
            stream.update(current_time)
        # draw to internal bg surface if available
        if bg_surface is not None:
            bg_surface.fill((0, 0, 0, 0))
            for stream in char_streams:
                stream.draw(bg_surface, font)
            screen_local.blit(bg_surface, (0, 0))
        else:
            for stream in char_streams:
                stream.draw(screen_local, font)

        # Randomly add new streams
        if len(char_streams) < max_char_count and random.random() < 0.02:
            available_columns = set(range(columns)) - set(stream.column for stream in char_streams)
            if available_columns:
                col = random.choice(list(available_columns))
                new_stream = CharStream(col)
                char_streams.append(new_stream)

        # Randomly remove some streams for dynamics
        if char_streams and random.random() < 0.01:
            char_streams.pop(random.randint(0, len(char_streams) - 1))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def update(current_time):
    """Update all streams (call once per frame)."""
    # advance each stream
    for stream in char_streams:
        stream.update(current_time)

    # occasionally add/remove streams for dynamics (same logic as standalone)
    if len(char_streams) < max_char_count and random.random() < 0.02:
        available_columns = set(range(columns)) - set(stream.column for stream in char_streams)
        if available_columns:
            col = random.choice(list(available_columns))
            new_stream = CharStream(col)
            char_streams.append(new_stream)

    if char_streams and random.random() < 0.01:
        char_streams.pop(random.randint(0, len(char_streams) - 1))


def draw(surface=None):
    """Draw streams onto the given surface (or internal screen if set).

    This will lazily create a module font if needed.
    """
    global module_font
    global module_is_pixel_font
    if surface is None:
        surface = screen
    if surface is None:
        return

    if module_font is None:
        # Try to load a bundled pixel font (ark-pixel) from the project's fonts/
        try:
            fonts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fonts'))
            candidates = glob.glob(os.path.join(fonts_dir, 'ark-pixel-12px-proportional-*.otf'))
            chosen = None
            if candidates:
                # prefer latin variant for ASCII; otherwise pick first
                for p in candidates:
                    if 'latin' in os.path.basename(p).lower():
                        chosen = p
                        break
                if chosen is None:
                    chosen = candidates[0]
                module_font = pygame.font.Font(chosen, font_size)
                module_is_pixel_font = True
        except Exception:
            module_font = None

    if module_font is None:
        try:
            module_font = pygame.font.SysFont('couriernew', font_size, bold=True)
            module_is_pixel_font = False
        except Exception:
            module_font = pygame.font.Font(None, font_size)
            module_is_pixel_font = False

    # draw into an internal transparent surface then blit so the background
    # is effectively transparent where no characters are drawn
    global bg_surface
    if bg_surface is not None:
        try:
            bg_surface.fill((0, 0, 0, 0))
            for stream in char_streams:
                stream.draw(bg_surface, module_font)
            surface.blit(bg_surface, (0, 0))
            return
        except Exception:
            pass

    # fallback: draw directly onto the provided surface
    for stream in char_streams:
        stream.draw(surface, module_font)

if __name__ == "__main__":
    main()
