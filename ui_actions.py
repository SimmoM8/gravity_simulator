import pygame
import pygame_gui
from config import *

def format_value(val):
    if val != 0 and (abs(val) >= 1e4 or abs(val) < 1e-3):
        return f"{val:.3e}"
    else:
        return str(val)

def handle_left_mouse_click(pos, ui, sim):
    sim_left = SIDEBAR_WIDTH
    sim_right = WINDOW_WIDTH - SIDEBAR_WIDTH
    sx, sy = pos
    wx, wy = sim.scene.camera.screen_to_world(sx, sy)
    # Check if click is within simulation area
    if not (sim_left <= sx < sim_right and 0 <= sy < WINDOW_HEIGHT):
        return

    # Check if clicked on an object
    for obj in sim.scene.objects:
        dist = ((wx - obj.x)**2 + (wy - obj.y)**2)**0.5
        if dist < obj.radius:
            sim.panning = False
            sim.dragging_object = obj
            select_object(obj, ui, sim)
            return

    # If no object was clicked, start panning
    deselect_object(ui, sim)
    sim.panning = True
    sim.last_pan_pos = pos

def drag_object(pos, sim):
    obj = sim.dragging_object

    wx, wy = sim.scene.camera.screen_to_world(pos[0], pos[1])

    if obj:
        # Ensure the object stays within the simulation area
        min_sx = SIDEBAR_WIDTH
        min_sy = HORIZONTAL_BAR_HEIGHT
        max_sx = WINDOW_WIDTH - SIDEBAR_WIDTH
        max_sy = WINDOW_HEIGHT - HORIZONTAL_BAR_HEIGHT

        # If the position is out of bounds, ignore the drag
        if pos[0] < min_sx or pos[0] > max_sx or pos[1] < min_sy or pos[1] > max_sy:
            return
        
        obj.x = wx
        obj.y = wy

def pan_camera(pos, sim):
    dx = pos[0] - sim.last_pan_pos[0]
    dy = pos[1] - sim.last_pan_pos[1]
    sim.scene.camera.pan(dx, dy)
    sim.last_pan_pos = pos

def handle_button_press(element, ui, sim):
    if handle_dialog_button_press(element, ui, sim):
        return
    if element == ui.add_object_button:
        add_object(ui, sim)
    elif element == ui.delete_object_button and sim.selected_object:
        launch_confirm_delete_dialog(ui, sim)
    elif element == ui.settings_button:
        ui.ui_manager.switch_page("right", "settings")
    elif element == ui.return_button_settings or element == ui.return_button_edit:
        ui.ui_manager.switch_page("right", "main")
        set_input_defaults(ui, DEFAULT_INPUTS)
    elif element == ui.pause_button:
        sim.paused = not sim.paused
        ui.pause_button.set_text("Resume" if sim.paused else "Pause")
    elif element == ui.reset_button:
        sim.scene.objects.clear()
        sim.selected_object = None
        sim.scene.object_id_counter = 0
        sim.elapsed_time = 0
        sim.scene.camera.reset()
        ui.ui_manager.switch_page("right", "main")
        set_input_defaults(ui, DEFAULT_INPUTS)
        refresh_object_list(ui, sim)
    elif element == ui.toggle_trail_button:
        sim.scene.trail_enabled = not getattr(sim.scene, "trail_enabled", False)
        ui.toggle_trail_button.set_text("Show Trail" if not sim.scene.trail_enabled else "Hide Trail")
    elif element == ui.toggle_velocity_vectors_button:
        sim.scene.vectors_enabled = not getattr(sim.scene, "vectors_enabled", True)
        text = "Show Velocity Vectors" if not sim.scene.vectors_enabled else "Hide Velocity Vectors"
        ui.toggle_velocity_vectors_button.set_text(text)
    elif element == ui.zoom_in_button:
        zoom_around_center(sim, True)
    elif element == ui.zoom_out_button:
        zoom_around_center(sim, False)

def zoom_around_center(sim, zoom_direction):
    screen_center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    sim.scene.camera.zoom_around_point(zoom_direction, screen_center)

def handle_dialog_button_press(element, ui, sim):
    dialog = getattr(ui, "confirm_dialog", None)
    if not dialog:
        return False
    if element == dialog.confirm_button:
        obj = getattr(dialog, "object_to_delete", None)
        if obj in sim.scene.objects:
            sim.scene.objects.remove(obj)
            deselect_object(ui, sim)
            refresh_object_list(ui, sim)
        dialog.kill()
        ui.confirm_dialog = None
        return True
    elif element == dialog.cancel_button:
        dialog.kill()
        ui.confirm_dialog = None
        return True
    return False

def handle_slider_change(element, ui, sim):
    if element == getattr(ui, "trail_length_slider", None):
        sim.scene.trail_length = int(ui.trail_length_slider.get_current_value())

def handle_selection(label, ui, sim):
    for obj in sim.scene.objects:
        full_label = f"{obj.id}"
        if hasattr(obj, "name") and obj.name:
            full_label += f" ({obj.name})"
        if full_label == label:
            select_object(obj, ui, sim)
            return
    deselect_object(ui, sim)

def select_object(obj, ui, sim):
    sim.ui_mode = "edit"
    sim.selected_object = obj
    ui.ui_manager.switch_page("right", "edit")
    ui.name_input_edit.set_text(str(getattr(obj, "name", "")))
    ui.mass_input_edit.set_text(format_value(float(getattr(obj, "mass", 0))))
    ui.radius_input_edit.set_text(format_value(float(getattr(obj, "radius", 0))))
    ui.vx_input_edit.set_text(str(float(getattr(obj, "vx", 0))))
    ui.vy_input_edit.set_text(str(float(getattr(obj, "vy", 0))))
    refresh_object_list(ui, sim)

def deselect_object(ui, sim):
    sim.ui_mode = ""
    sim.selected_object = None
    ui.ui_manager.switch_page("right", "main")
    set_input_defaults(ui, DEFAULT_INPUTS)
    refresh_object_list(ui, sim)

def update_selected_object(ui, sim):
    obj = sim.selected_object
    if obj:
        obj.name = ui.name_input_edit.get_text()
        try:
            val = float(ui.mass_input_edit.get_text())
            obj.mass = min(max(MASS_MIN, val), MASS_MAX)
        except ValueError:
            pass
        try:
            r = float(ui.radius_input_edit.get_text())
            obj.radius = min(max(RADIUS_MIN, r), RADIUS_MAX)
        except ValueError:
            pass
        try:
            obj.vx = max(min(float(ui.vx_input_edit.get_text()), VELOCITY_MAX), VELOCITY_MIN)
        except Exception:
            pass
        try:
            obj.vy = max(min(float(ui.vy_input_edit.get_text()), VELOCITY_MAX), VELOCITY_MIN)
        except Exception:
            pass
        refresh_object_list(ui, sim)

def launch_confirm_delete_dialog(ui, sim):
    obj = sim.selected_object
    dialog = pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect((WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 75), (300, 150)),
        manager=ui.manager,
        window_title='Confirm Deletion',
        action_long_desc=f"Are you sure you want to delete '{getattr(obj, 'name', obj.id)}'?",
        action_short_name='Delete',
        blocking=True
    )
    dialog.object_to_delete = obj
    ui.confirm_dialog = dialog

def refresh_object_list(ui, sim):
    items = []
    for obj in sim.scene.objects:
        label = f"{obj.id}"
        if hasattr(obj, "name") and obj.name:
            label += f" ({obj.name})"
        items.append(label)
    ui.object_list.set_item_list(items)
    sel = sim.selected_object
    if sel:
        label = f"{sel.id}"
        if hasattr(sel, "name") and sel.name:
            label += f" ({sel.name})"
        ui.object_list.selected_item = label
    else:
        ui.object_list.selected_item = None

def add_object(ui, sim):
    """Add a new object with properties from UI and a unique ID."""
    name = ui.name_input_add.get_text()
    object_id_counter = sim.scene.object_id_counter

    # Fallback default values
    if not name:
        name = DEFAULT_INPUTS["name"]
    try:
        val = float(ui.mass_input_add.get_text())
        mass = min(max(MASS_MIN, val), MASS_MAX)
    except Exception:
        mass = DEFAULT_INPUTS["mass"]
    if not ui.mass_input_add.get_text().strip():
        mass = DEFAULT_INPUTS["mass"]
    try:
        r = float(ui.radius_input_add.get_text())
        radius = int(min(max(RADIUS_MIN, r), RADIUS_MAX))
    except Exception:
        radius = DEFAULT_INPUTS["radius"]
    if not ui.radius_input_add.get_text().strip():
        radius = DEFAULT_INPUTS["radius"]
    try:
        vx = max(min(float(ui.vx_input_add.get_text()), VELOCITY_MAX), VELOCITY_MIN)
    except Exception:
        vx = 0
    try:
        vy = max(min(float(ui.vy_input_add.get_text()), VELOCITY_MAX), VELOCITY_MIN)
    except Exception:
        vy = 0

    camera = sim.scene.camera

    # Screen center in pixels
    screen_center_x = WINDOW_WIDTH // 2
    screen_center_y = WINDOW_HEIGHT // 2

    # Convert to world coordinates for object initial position
    wx, wy = camera.screen_to_world(screen_center_x, screen_center_y)

    shock_absorption = 0.001 * mass
    obj = type('Object', (), {})()
    obj.id = object_id_counter
    obj.name = name
    obj.x = wx
    obj.y = wy
    obj.vx = vx
    obj.vy = vy
    obj.mass = mass
    obj.radius = radius
    obj.shock_absorption = shock_absorption
    obj.color = (200, 50, 50)
    sim.scene.objects.append(obj)
    sim.scene.object_id_counter += 1
    refresh_object_list(ui, sim)
    sim.selected_object = None

def set_input_defaults(ui, defaults=DEFAULT_INPUTS):
    ui.ui_manager.switch_page("right", "main")
    ui.name_input_add.set_text(str(defaults["name"]))
    ui.mass_input_add.set_text(str(defaults["mass"]))
    ui.radius_input_add.set_text(str(defaults["radius"]))
    ui.vx_input_add.set_text(str(defaults["vx"]))
    ui.vy_input_add.set_text(str(defaults["vy"]))