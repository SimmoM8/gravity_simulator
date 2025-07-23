WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 700
HORIZONTAL_BAR_HEIGHT = 50
SIDEBAR_WIDTH = 200
BACKGROUND_COLOR = (30, 30, 30)
VECTOR_FIELD_COLOR = (100, 200, 100)
FPS = 60
GRID_SIZE = 20
TRAIL_DEFAULT_LENGTH = 100
PADDING = 0
MARGIN = 10
LABEL_INPUT_GAP = 500
VELOCITY_VECTOR_COLOR = (0, 0, 255)

PANEL_CONFIG = {
    "top": {
        "width": WINDOW_WIDTH,
        "height": HORIZONTAL_BAR_HEIGHT,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "horizontal",
    },
    "bottom": {
        "width": WINDOW_WIDTH,
        "height": HORIZONTAL_BAR_HEIGHT,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "horizontal",
    },
    "left": {
        "width": SIDEBAR_WIDTH,
        "height": WINDOW_HEIGHT,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "vertical",
    },
    "right": {
        "width": SIDEBAR_WIDTH,
        "height": WINDOW_HEIGHT,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "vertical",
    },
}

MASS_MIN = 1
MASS_MAX = 1e40
RADIUS_MIN = 1
RADIUS_MAX = 1e12
VELOCITY_MIN = -1e10
VELOCITY_MAX = 1e10

DEFAULT_INPUTS = {
    "name": "Earth",
    "mass": 5.972e24,
    "radius": 6.371e6,
    "vx": 10,
    "vy": 10,
    "speed_multiplier": 1.0,
    # Add future inputs here
}

G = 6.67430e-11  # m³/kg/s² (real-world gravitational constant)

# Coefficient of restitution for object-object collisions
COEFFICIENT_OF_RESTITUTION = 0.1  # 1.0 means perfectly elastic collision