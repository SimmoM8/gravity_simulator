from config import PANEL_CONFIG, WINDOW_WIDTH, WINDOW_HEIGHT

def get_panel_rect(panel_name):
    import pygame
    if panel_name == "top":
        # Top panel: full width, fixed height at top
        return pygame.Rect(
            0,
            0,
            WINDOW_WIDTH,
            PANEL_CONFIG["top"]["height"]
        )
    elif panel_name == "bottom":
        # Bottom panel: full width, fixed height at bottom
        return pygame.Rect(
            0,
            WINDOW_HEIGHT - PANEL_CONFIG["bottom"]["height"],
            WINDOW_WIDTH,
            PANEL_CONFIG["bottom"]["height"]
        )
    elif panel_name == "left":
        # Left panel: fixed width, fills between top and bottom panels
        top_h = PANEL_CONFIG["top"]["height"]
        bottom_h = PANEL_CONFIG["bottom"]["height"]
        return pygame.Rect(
            0,
            top_h,
            PANEL_CONFIG["left"]["width"],
            WINDOW_HEIGHT - top_h - bottom_h
        )
    elif panel_name == "right":
        # Right panel: fixed width, fills between top and bottom panels, aligned right
        top_h = PANEL_CONFIG["top"]["height"]
        bottom_h = PANEL_CONFIG["bottom"]["height"]
        width = PANEL_CONFIG["right"]["width"]
        return pygame.Rect(
            WINDOW_WIDTH - width,
            top_h,
            width,
            WINDOW_HEIGHT - top_h - bottom_h
        )
    else:
        raise ValueError(f"Unknown panel name: {panel_name}")

def build_panel(manager, panel_name):
    from ui_panels import PANEL_CLASSES
    from components import auto_layout_elements
    from ui_page import UIPage
    from pygame_gui.elements import UIPanel
    import pygame

    # Instantiate the appropriate panel class
    panel_class = PANEL_CLASSES[panel_name]
    panel_instance = panel_class()

    # Use get_panel_rect for the panel's relative_rect
    relative_rect = get_panel_rect(panel_name)
    panel = UIPanel(relative_rect=relative_rect, manager=manager, starting_height=1)

    layout = PANEL_CONFIG[panel_name]["layout"]
    padding = PANEL_CONFIG[panel_name]["padding"]
    margin = PANEL_CONFIG[panel_name]["margin"]

    pages_dict = {}

    # Iterate through all pages in the panel
    for page_name, element_defs in panel_instance.pages.items():
        # Create UI components for each page
        elements = auto_layout_elements(manager, element_defs, relative_rect, layout)
        container = panel.get_container()
        # Add each UI component to the single UIPanel
        for element in elements:
            container.add_element(element)
        # Store UIPage with just elements for this page
        pages_dict[page_name] = UIPage(elements)

    return panel, pages_dict
