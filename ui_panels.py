# ui_panels.py
# This file defines the UI structure (panels and their pages), not rendering.

class RightPanel:
    def __init__(self):
        self.pages = {
            "main": [
                {"type": "label", "text": "Menu", "name": "menu_label"},
                {"type": "button", "text": "Add Object", "name": "add_object_button"},
                {"type": "text_input", "name": "name_input", "label": "Name:"},
                {"type": "text_input", "name": "mass_input", "label": "Mass:"},
                {"type": "text_input", "name": "radius_input", "label": "Radius:"},
                {"type": "button", "text": "Settings", "name": "settings_button"},
            ],
            "settings": [
                {"type": "label", "text": "Settings", "name": "settings_label"},
                {"type": "button", "text": "Toggle Field", "name": "toggle_field_button"},
                {"type": "slider", "start_value": 50, "min_val": 0, "max_val": 100, "name": "field_slider", "label": "Trail Length:"},
                {"type": "button", "text": "Toggle Trail", "name": "toggle_trail_button"},
                {"type": "button", "text": "Return", "name": "return_button"},
            ],
            "edit": [
                {"type": "label", "text": "Edit Object", "name": "edit_object_label"},
                {"type": "button", "text": "Delete Object", "name": "delete_object_button"},
                {"type": "button", "text": "Return", "name": "return_button_edit"},
            ]
        }

class LeftPanel:
    def __init__(self):
        self.pages = {
            "main": [
                {"type": "selection_list", "name": "object_list", "item_list": []}
            ]
        }

class TopPanel:
    def __init__(self):
        self.pages = {
            "main": [
                {"type": "label", "text": "Gravity Simulator", "name": "title_label"},
                {"type": "button", "text": "Help", "name": "help_button", "align": "right"},
            ]
        }

class BottomPanel:
    def __init__(self):
        self.pages = {
            "main": [
                {"type": "button", "text": "Pause", "name": "pause_button", "align": "center"},
                {"type": "button", "text": "Reset", "name": "reset_button", "align": "center"},
                {"type": "text_input", "name": "time_step_input", "label": "Time Step:", "align": "right"},
            ]
        }

# Optional: for easy import/lookup
PANEL_CLASSES = {
    "top": TopPanel,
    "bottom": BottomPanel,
    "left": LeftPanel,
    "right": RightPanel
}