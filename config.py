WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 700
TOOLBAR_WIDTH = 200
LEFT_SIDEBAR_WIDTH = 200
BACKGROUND_COLOR = (30, 30, 30)
VECTOR_FIELD_COLOR = (100, 200, 100)
FPS = 60
GRID_SIZE = 20
TRAIL_DEFAULT_LENGTH = 100
PADDING = 0
MARGIN = 10
LABEL_INPUT_GAP = 500

PANEL_CONFIG = {
    "top": {
        "width": WINDOW_WIDTH,
        "height": 50,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "horizontal",
    },
    "bottom": {
        "width": WINDOW_WIDTH,
        "height": 50,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "horizontal",
    },
    "left": {
        "width": LEFT_SIDEBAR_WIDTH,
        "height": WINDOW_HEIGHT,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "vertical",
    },
    "right": {
        "width": TOOLBAR_WIDTH,
        "height": WINDOW_HEIGHT,
        "padding": PADDING,
        "margin": MARGIN,
        "background_color": BACKGROUND_COLOR,
        "layout": "vertical",
    },
}

DEFAULT_INPUTS = {
    "name": "",
    "mass": 10,
    "radius": 10,
    # Add future inputs here
}