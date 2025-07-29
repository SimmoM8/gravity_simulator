from ui.panel_builder import build_panel
import pygame
import pygame_gui
from ui.ui_panels import PANEL_CLASSES
from setup.config import SIDEBAR_WIDTH

class UIManager:
    def __init__(self, manager):
        self.panels = {}
        # Build each panel once with all its pages and elements
        for panel_name, panel_cls in PANEL_CLASSES.items():
            panel, pages = build_panel(manager, panel_name)
            self.panels[panel_name] = {
                "panel": panel,
                "pages": pages
            }

        # Dictionary to track the currently visible page per panel
        self.current_pages = {}
        # Dictionary to map element names to element instances for quick access
        self.elements_by_name = {}

        # Initially hide all pages in all panels to start with a clean UI
        for panel_info in self.panels.values():
            for page in panel_info["pages"].values():
                page.hide()

        # Populate elements_by_name dictionary by iterating over all elements in all pages
        # This allows quick lookup of elements by their unique element_name attribute
        for panel_info in self.panels.values():
            for page in panel_info["pages"].values():
                for element in page.elements:
                    if hasattr(element, 'element_name'):
                        self.elements_by_name[element.element_name] = element

        # Show the default 'main' page on each panel at startup to provide a starting UI
        for panel_name in self.panels.keys():
            self.switch_page(panel_name, "main")

        # Create floating zoom buttons anchored to the bottom right of the window
        self.zoom_in_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((-60 - SIDEBAR_WIDTH, -185), (40, 30)),
            text='+',
            manager=manager,
            object_id="zoom_in_button",
            anchors={
                'left': 'right',
                'right': 'right',
                'top': 'bottom',
                'bottom': 'bottom'
            }
        )

        self.zoom_out_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((-60 -SIDEBAR_WIDTH, -150), (40, 30)),
            text='–',
            manager=manager,
            object_id="zoom_out_button",
            anchors={
                'left': 'right',
                'right': 'right',
                'top': 'bottom',
                'bottom': 'bottom'
            }
        )

        # Register buttons for easy access via ui.get(...)
        self.elements_by_name["zoom_in_button"] = self.zoom_in_button
        self.elements_by_name["zoom_out_button"] = self.zoom_out_button

    def switch_page(self, panel_name, page_name):
        # Get the currently active page for this panel
        current = self.current_pages.get(panel_name)
        if current:
            # Hide the current page before switching
            current.hide()

        # Retrieve the new page object to show
        new_page = self.panels[panel_name]["pages"][page_name]
        # Show the new page
        new_page.show()
        # Update the current page tracking for this panel
        self.current_pages[panel_name] = new_page

    def current_page(self, panel_name):
        return self.current_pages.get(panel_name)

    def get_element(self, panel_name, element_name):
        # Get the currently active page for the panel
        page = self.current_pages.get(panel_name)
        if not page:
            raise ValueError(f"No current page set for panel '{panel_name}'")

        # Search for the element by name within the current page's elements
        for element in page.elements:
            if hasattr(element, 'element_name') and element.element_name == element_name:
                return element

        # If element not found, raise an error
        raise ValueError(f"Element '{element_name}' not found in panel '{panel_name}'")

    def get(self, name):
        return self.elements_by_name.get(name)