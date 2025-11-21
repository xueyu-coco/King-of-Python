import pygame
import random
import math

# Window size settings (defaults). Do NOT create a display at import time;
# creating a display at import causes side-effects when this module is imported
# from other code (like `main.py`). `main()` will initialize pygame and create
# the screen instead.
cw, ch = 1200, 800
screen = None
bg_surface = None

# Color definitions: purple-tone palette for code-style rain
# Use a variety of purple/pink/lavender tones so streams vary while
# remaining in the purple family.
PALETTE = [
    (181, 104, 255),
]
BLACK = (0, 0, 0)

# Alpha scale for stream transparency (0.0 = fully transparent, 1.0 = original)
# Increase this value to make the streams more opaque (less transparent).
ALPHA_SCALE = 0.85

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
font = None
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
        for i, char in enumerate(self.chars):
            # Character color gradient - head is brightest, tail fades
            if char['bright']:
                # head uses a much brighter version of the stream base color
                color = tuple(min(255, c + 120) for c in self.base_color)
                # brighter head alpha (scaled)
                alpha = int(230 * ALPHA_SCALE)
            else:
                # Compute brightness based on position in the stream; top characters are brighter
                raw = 1.0 - (i / self.stream_length)
                brightness = max(0.15, 0.95 * raw)
                color = (
                    int(self.base_color[0] * brightness),
                    int(self.base_color[1] * brightness),
                    int(self.base_color[2] * brightness)
                )
                # overall alpha scaled by brightness (make slightly stronger)
                alpha = int(245 * brightness * ALPHA_SCALE)

            # 绘制字符（使用 alpha 调低亮度）
            if 0 <= char['y'] <= ch:
                # render base text surface
                text_surf = font.render(char['value'], True, color).convert_alpha()
                # apply alpha and scale
                scale = char.get('scale', 1.0)
                sw = max(1, int(text_surf.get_width() * scale))
                sh = max(1, int(text_surf.get_height() * scale))

                # prepare scaled surfaces for base, outline and glow
                try:
                    base_scaled = pygame.transform.smoothscale(text_surf, (sw, sh)) if (sw != text_surf.get_width() or sh != text_surf.get_height()) else text_surf
                except Exception:
                    base_scaled = pygame.transform.scale(text_surf, (sw, sh)) if (sw != text_surf.get_width() or sh != text_surf.get_height()) else text_surf

                # Alpha settings and compute blit positions
                base_alpha = alpha
                blit_x = int(self.x + (font_size - sw) / 2)
                blit_y = int(char['y'] - (sh - font_size))

                # draw the base character (no outline, no glow)
                base_scaled.set_alpha(base_alpha)
                screen.blit(base_scaled, (blit_x, blit_y))

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

def handle_resize(event_or_size):
    """Update internal size/column settings. Accepts a pygame VIDEORESIZE event
    or a (w, h) tuple. This will NOT create a display surface (no side effects).
    """
    global cw, ch, columns
    if hasattr(event_or_size, 'w') and hasattr(event_or_size, 'h'):
        w, h = event_or_size.w, event_or_size.h
    else:
        w, h = event_or_size
    cw, ch = w, h
    columns = max(1, cw // font_size)
    create_streams()

def init(width=None, height=None):
    """Initialize background subsystem. Signature accepts the same
    optional parameters as `backround_1.init(width, height, create_display=False)`
    so the module can be embedded by `main.py` without raising due to
    unexpected kwargs. If create_display is True this will also create a
    display surface.
    """
    global cw, ch, columns, font, screen, bg_surface
    # accept legacy signature create_display via kwargs if passed
    # (main.py may call init(WIDTH, HEIGHT, create_display=False))
    # so we detect and ignore unknown params in positional call.
    cw = int(width) if width is not None else cw
    ch = int(height) if height is not None else ch
    columns = max(1, cw // font_size)
    # create display surface only when requested
    # note: some callers pass create_display as a keyword; support both
    # positional and keyword by reading from local frame if available
    try:
        # try to inspect calling args (if create_display provided as kw)
        import inspect
        frame = inspect.currentframe()
        args, _, kwargs, _ = inspect.getargvalues(frame)
    except Exception:
        kwargs = {}
    create_display = kwargs.get('create_display', False)
    # if create_display requested, initialize pygame display
    if create_display:
        try:
            pygame.init()
            screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
        except Exception:
            screen = None
    # recreate internal bg surface if we have a screen
    try:
        if screen is not None:
            bg_surface = pygame.Surface((cw, ch), pygame.SRCALPHA)
    except Exception:
        bg_surface = None
    # ensure font is created (requires pygame.font.init() which is
    # available after pygame.init())
    try:
        font = pygame.font.SysFont('couriernew', font_size, bold=True)
    except Exception:
        font = pygame.font.Font(None, font_size)
    create_streams()

def set_surface(surface):
    """Set an external surface as the rendering target (safe for embedding).

    This mirrors the API in `backround_1` so `main.py` can call
    `background.set_surface(screen)` for either background module.
    """
    global screen, cw, ch, columns, bg_surface
    screen = surface
    try:
        w, h = surface.get_size()
        cw, ch = int(w), int(h)
        columns = max(1, cw // font_size)
    except Exception:
        pass
    try:
        bg_surface = pygame.Surface((cw, ch), pygame.SRCALPHA)
    except Exception:
        bg_surface = None
    create_streams()

def update(current_time):
    """Update background animation state. Pass pygame.time.get_ticks()."""
    for stream in char_streams:
        stream.update(current_time)

    # Occasionally add streams when under the max count (same as standalone)
    if len(char_streams) < max_char_count and random.random() < 0.02:
        available_columns = set(range(columns)) - set(s.column for s in char_streams)
        if available_columns:
            col = random.choice(list(available_columns))
            new_stream = CharStream(col)
            char_streams.append(new_stream)

    # Randomly remove some streams for dynamics
    if char_streams and random.random() < 0.01:
        char_streams.pop(random.randint(0, len(char_streams) - 1))

    # Additionally spawn occasional short single-column streams so that
    # isolated drops still occur even after most streams have fallen.
    # Use a higher spawn chance when no streams are present.
    spawn_chance = 0.06 if not char_streams else 0.015
    if random.random() < spawn_chance:
        available_columns = set(range(columns)) - set(s.column for s in char_streams)
        if available_columns:
            col = random.choice(list(available_columns))
            s = CharStream(col)
            # make it a short transient stream
            s.stream_length = random.randint(2, 6)
            # rebuild initial chars to match the short length
            s.chars = []
            for i in range(s.stream_length):
                chval = {
                    'value': random.choice(char_arr),
                    'y': -i * font_size,
                    'bright': False,
                    'scale': random.uniform(SCALE_MIN, SCALE_MAX),
                }
                s.chars.append(chval)
            # make short streams slightly faster
            s.speed = random.uniform(max(stream_speed_min, 3.5), stream_speed_max + 2)
            char_streams.append(s)

def draw(surface):
    """Draw background onto the provided surface."""
    if surface is None:
        return
    # create font on-demand if not present
    global font
    if font is None:
        try:
            font = pygame.font.SysFont('couriernew', font_size, bold=True)
        except Exception:
            font = pygame.font.Font(None, font_size)
    # clear surface area for background drawing if needed (caller may clear)
    # Draw streams
    for stream in char_streams:
        stream.draw(surface, font)

def main():
    global char_streams, screen, cw, ch

    # Initialize pygame and create the display here (so importing this
    # module does not open a window as a side-effect).
    pygame.init()
    screen = pygame.display.set_mode((cw, ch), pygame.RESIZABLE)
    pygame.display.set_caption("Matrix Digital Rain")

    # Create font
    font = pygame.font.SysFont('couriernew', font_size, bold=True)

    # Create initial streams
    create_streams()

    clock = pygame.time.Clock()
    running = True

    # fill screen once to initialize
    screen.fill(BLACK)

    while running:
        current_time = pygame.time.get_ticks()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen each frame (no motion trail)
        screen.fill(BLACK)

        # Update and draw all streams
        for stream in char_streams:
            stream.update(current_time)
            stream.draw(screen, font)

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

if __name__ == "__main__":
    main()
