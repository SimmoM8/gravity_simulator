import pygame
import pygame_gui
from ui.ui_actions import *
from setup.presets import get_preset_names, get_preset_by_name

def handle_event(event, ui, sim):
    manager = ui.manager

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            handle_left_mouse_click(event.pos, ui, sim)

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            sim.dragging_object = None
            sim.panning = False
            sim.last_pan_pos = None

    elif event.type == pygame.MOUSEMOTION:
        if sim.dragging_object:
            drag_object(event.pos, sim)
        elif sim.panning:
            pan_camera(event.pos, sim)

    elif event.type == pygame.MOUSEWHEEL:
        mouse_pos = pygame.mouse.get_pos()
        if event.y > 0:
            sim.scene.camera.zoom_around_point(True, mouse_pos)
        elif event.y < 0:
            sim.scene.camera.zoom_around_point(False, mouse_pos)

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
            zoom_around_center(sim, True)
        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
            zoom_around_center(sim, False)

    elif event.type == pygame.USEREVENT:
        if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            element = event.ui_element
            # If currently editing an object, update its properties
            if sim.ui_mode == "edit" and element in (
                ui.mass_input_edit,
                ui.radius_input_edit,
                ui.name_input_edit,
                ui.vx_input_edit,
                ui.vy_input_edit,
            ):
                update_selected_object(ui, sim)
            # If speed multiplier input changed, update speed multiplier
            elif element == ui.speed_multiplier_input:
                try:
                    sim.speed_multiplier = float(element.get_text())
                except ValueError:
                    sim.speed_multiplier = 1.0  # default fallback

        elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            handle_button_press(event.ui_element, ui, sim)

        elif event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            handle_selection(event.text, ui, sim)

        elif event.user_type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION:
            deselect_object(ui, sim)

        elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            handle_slider_change(event.ui_element, ui, sim)

        elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            element = event.ui_element
            if element == ui.preset_dropdown:  # Adjust to your dropdown element name
                print(f"element: {element}")
                print(f"Dropdown changed: {element.selected_option}")
                selected_name = element.selected_option
                print(f"Selected preset: {selected_name}")
                # Get the preset data for the selected option
                preset_data = get_preset_by_name(selected_name[0])  # You need this helper
                if preset_data:
                    ui.name_input_add.set_text(preset_data["name"])
                    ui.mass_input_add.set_text(str(float(preset_data["mass"])))
                    ui.radius_input_add.set_text(str(float(preset_data["radius"])))
                    ui.vx_input_add.set_text(str(float(preset_data.get("vx", 0))))
                    ui.vy_input_add.set_text(str(float(preset_data.get("vy", 0))))

    manager.process_events(event)