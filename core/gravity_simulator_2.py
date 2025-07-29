import pygame
import pygame_gui
from setup.config import *
from core.scene import Scene
from ui.ui_events import handle_event
from ui.ui_actions import set_input_defaults
from ui.ui_manager import UIManager


class UIState:
    def __init__(self, manager, ui_manager):
        self.manager = manager
        self.ui_manager = ui_manager

        self.object_list = ui_manager.get("object_list")
        self.menu_label = ui_manager.get("menu_label")
        self.name_input_add = ui_manager.get("name_input_add")
        self.mass_input_add = ui_manager.get("mass_input_add")
        self.radius_input_add = ui_manager.get("radius_input_add")
        self.vx_input_add = ui_manager.get("vx_input_add")
        self.vy_input_add = ui_manager.get("vy_input_add")
        self.name_input_edit = ui_manager.get("name_input_edit")
        self.mass_input_edit = ui_manager.get("mass_input_edit")
        self.radius_input_edit = ui_manager.get("radius_input_edit")
        self.vx_input_edit = ui_manager.get("vx_input_edit")
        self.vy_input_edit = ui_manager.get("vy_input_edit")
        self.field_toggle_button = ui_manager.get("field_toggle_button")
        self.pause_button = ui_manager.get("pause_button")
        self.reset_button = ui_manager.get("reset_button")
        self.toggle_trail_button = ui_manager.get("toggle_trail_button")
        self.trail_length_slider = ui_manager.get("trail_length_slider")
        self.toggle_velocity_vectors_button = ui_manager.get("toggle_velocity_vectors_button")
        self.return_button_settings = ui_manager.get("return_button_settings")
        self.return_button_edit = ui_manager.get("return_button_edit")
        self.add_object_button = ui_manager.get("add_object_button")
        self.delete_object_button = ui_manager.get("delete_object_button")
        self.settings_button = ui_manager.get("settings_button")
        self.zoom_in_button = ui_manager.get("zoom_in_button")
        self.zoom_out_button = ui_manager.get("zoom_out_button")
        self.speed_multiplier_input = ui_manager.get("speed_multiplier_input")
        self.preset_dropdown = ui_manager.get("preset_dropdown")


class SimulationState:
    def __init__(self):
        self.scene = Scene()
        self.ui_mode = ""
        self.selected_object = None
        self.dragging_object = None
        self.paused = False
        self.confirm_dialog = None
        self.speed_multiplier = 1.0
        self.elapsed_time = 0
        self.panning = False
        self.last_pan_pos = None


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Gravity Simulator 2")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 20)
        self.header_font = pygame.font.SysFont(None, 28)

        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.ui_manager = UIManager(self.manager)

        self.ui = UIState(self.manager, self.ui_manager)
        self.sim = SimulationState()

        set_input_defaults(self.ui, DEFAULT_INPUTS)

    def run(self):        
        running = True

        while running:
            time_delta = self.clock.tick(FPS) / 1000.0
            try:
                if self.sim.speed_multiplier <= 0:
                    self.sim.speed_multiplier = 1.0  # Prevent zero or negative speeds
            except (ValueError, AttributeError):
                speed_multiplier = 1.0  # Default if invalid input

            effective_time_delta = time_delta * self.sim.speed_multiplier

            self.screen.fill(BACKGROUND_COLOR)

            

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    handle_event(event, self.ui, self.sim)

            # Update your simulation with physics etc.    
            if not self.sim.paused:

                self.sim.elapsed_time += effective_time_delta
                self.sim.scene.update(effective_time_delta)

            self.sim.scene.draw(self.screen, self.font, self.sim)

            # Calculate FPS
            fps = self.clock.get_fps()

            # Update the UI status label here
            status_label = self.ui_manager.get("status_label")
            if status_label:
                formatted_time = self.format_elapsed_time(self.sim.elapsed_time)
                fps = self.clock.get_fps()
                status_label.set_text(f"FPS: {int(fps)} | Time: {formatted_time}")
                status_label.border_width = {"left": 0, "right": 0, "top": 0, "bottom": 0}


            # Update and draw UI
            self.manager.update(effective_time_delta)
            self.manager.draw_ui(self.screen)

            pygame.display.flip()

    def format_elapsed_time(self, seconds: float) -> str:
        intervals = (
            ('yr', 60 * 60 * 24 * 7 * 52),
            ('wk', 60 * 60 * 24 * 7),
            ('d', 60 * 60 * 24),
            ('hr', 60 * 60),
            ('min', 60),
            ('s', 1),
        )

        remaining = int(seconds)
        parts = []

        for name, count in intervals:
            value = remaining // count
            if value > 0:
                parts.append(f"{value} {name}")
                remaining %= count

        # If no parts added, show seconds (handles less than 1 second)
        if not parts:
            return "0 s"

        return ' '.join(parts)

        pygame.quit()