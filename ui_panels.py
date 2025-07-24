# ui_panels.py
# This file defines the UI structure (panels and their pages), not rendering.
class RightPanel:
    def __init__(self):
        self.pages = {
            "main": [
                {"type": "label", "text": "Menu", "name": "menu_label"},
                {"type": "button", "text": "Add Object", "name": "add_object_button"},
                {"type": "dropdown", "name": "preset_dropdown", "options_source": "preset_objects", "label": "Presets:"},
                {"type": "text_input", "name": "name_input_add", "label": "Name:"},
                {"type": "text_input", "name": "mass_input_add", "label": "Mass:"},
                {"type": "text_input", "name": "radius_input_add", "label": "Radius:"},
                {"type": "text_input", "name": "vx_input_add", "label": "Velocity X:"},
                {"type": "text_input", "name": "vy_input_add", "label": "Velocity Y:"},
                {"type": "button", "text": "Settings", "name": "settings_button"},
            ],
            "settings": [
                {"type": "label", "text": "Settings", "name": "settings_label"},
                {"type": "button", "text": "Toggle Field", "name": "toggle_field_button"},
                {"type": "slider", "start_value": 3, "min_val": 1, "max_val": 20, "step": 1, "name": "trail_length_slider", "label": "Trail Age (s):"},
                {"type": "button", "text": "Hide Trail", "name": "toggle_trail_button"},
                {"type": "button", "text": "Show Velocity Vectors", "name": "toggle_velocity_vectors_button"},
                {"type": "button", "text": "Return", "name": "return_button_settings"},
            ],
            "edit": [
                {"type": "label", "text": "Edit Object", "name": "edit_object_label"},
                {"type": "button", "text": "Delete Object", "name": "delete_object_button"},
                {"type": "text_input", "name": "name_input_edit", "label": "Name:"},
                {"type": "text_input", "name": "mass_input_edit", "label": "Mass:"},
                {"type": "text_input", "name": "radius_input_edit", "label": "Radius:"},
                {"type": "text_input", "name": "vx_input_edit", "label": "Velocity X:"},
                {"type": "text_input", "name": "vy_input_edit", "label": "Velocity Y:"},
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
                {"type": "text_input", "name": "speed_multiplier_input", "label": "Speed Multiplier:", "align": "right"},
                {"type": "text_box", "text": "<p align='left'>FPS: 0 | Time: 0.0s</p>", "name": "status_label", "align": "left", "width": 400, "text_alignment": "left"},

            ]
        }

# Optional: for easy import/lookup
PANEL_CLASSES = {
    "top": TopPanel,
    "bottom": BottomPanel,
    "left": LeftPanel,
    "right": RightPanel
}