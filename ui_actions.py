import pygame
import pygame_gui
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_WIDTH, LEFT_SIDEBAR_WIDTH, DEFAULT_INPUTS
)

def handle_mouse_click(pos, ui, sim):
    sim_left = LEFT_SIDEBAR_WIDTH
    sim_right = WINDOW_WIDTH - TOOLBAR_WIDTH
    x, y = pos
    if not (sim_left <= x < sim_right and 0 <= y < WINDOW_HEIGHT):
        return
    for obj in sim["objects"]:
        dist = ((x - obj["x"])**2 + (y - obj["y"])**2)**0.5
        if dist < obj["radius"]:
            sim["dragging_object"] = obj
            select_object(obj, ui, sim)
            return
    deselect_object(ui, sim)

def handle_mouse_drag(pos, ui, sim):
    obj = sim.get("dragging_object")
    if obj:
        min_x = LEFT_SIDEBAR_WIDTH + obj["radius"]
        max_x = WINDOW_WIDTH - TOOLBAR_WIDTH - obj["radius"]
        min_y = obj["radius"]
        max_y = WINDOW_HEIGHT - obj["radius"]
        obj["x"] = max(min_x, min(max_x, pos[0]))
        obj["y"] = max(min_y, min(max_y, pos[1]))

def handle_button_press(element, ui, sim):
    if handle_dialog_button_press(element, ui, sim):
        return
    if element == ui["add_object_button"]:
        add_object(ui, sim)
    elif element == ui["delete_object_button"] and sim["selected_object"]:
        launch_confirm_delete_dialog(ui, sim)
    elif element == ui["settings_button"]:
        ui["ui_manager"].switch_page("right", "settings")
    elif element == ui["return_button_settings"] or element == ui["return_button_edit"]:
        ui["ui_manager"].switch_page("right", "main")
        set_input_defaults(ui, DEFAULT_INPUTS)
    elif element == ui["pause_button"]:
        sim["paused"] = not sim["paused"]
        ui["pause_button"].set_text("Resume" if sim["paused"] else "Pause")
    elif element == ui["reset_button"]:
        sim["objects"].clear()
        sim["selected_object"] = None
        ui["ui_manager"].switch_page("right", "main")
        set_input_defaults(ui, DEFAULT_INPUTS)
        refresh_object_list(ui, sim)
    elif element == ui["toggle_trail_button"]:
        sim["trail_enabled"] = not sim.get("trail_enabled", False)
        ui["toggle_trail_button"].set_text("Show Trail" if not sim["trail_enabled"] else "Hide Trail")
    elif element == ui["toggle_velocity_vectors_button"]:
        sim["vectors_enabled"] = not sim.get("vectors_enabled", True)
        text = "Show Velocity Vectors" if not sim["vectors_enabled"] else "Hide Velocity Vectors"
        ui["toggle_velocity_vectors_button"].set_text(text)

def handle_dialog_button_press(element, ui, sim):
    dialog = ui.get("confirm_dialog")
    if not dialog:
        return False
    if element == dialog.confirm_button:
        obj = getattr(dialog, "object_to_delete", None)
        if obj in sim["objects"]:
            sim["objects"].remove(obj)
            deselect_object(ui, sim)
            refresh_object_list(ui, sim)
        dialog.kill()
        ui["confirm_dialog"] = None
        return True
    elif element == dialog.cancel_button:
        dialog.kill()
        ui["confirm_dialog"] = None
        return True
    return False

def handle_slider_change(element, ui, sim):
    if element == ui.get("trail_length_slider"):
        sim["trail_length"] = int(ui["trail_length_slider"].get_current_value())
        for obj in sim["objects"]:
            if "trail" in obj:
                obj["trail"] = obj["trail"][-sim["trail_length"]:]

def handle_selection(label, ui, sim):
    for obj in sim["objects"]:
        full_label = f"{obj['id']}"
        if obj.get("name"):
            full_label += f" ({obj['name']})"
        if full_label == label:
            select_object(obj, ui, sim)
            return
    deselect_object(ui, sim)

def select_object(obj, ui, sim):
    sim["ui_mode"] = "edit"
    sim["selected_object"] = obj
    ui["ui_manager"].switch_page("right", "edit")
    ui["name_input_edit"].set_text(str(obj["name"]))
    ui["mass_input_edit"].set_text(str(obj["mass"]))
    ui["radius_input_edit"].set_text(str(int(obj["radius"])))
    ui["vx_input_edit"].set_text(str(obj["vx"]))
    ui["vy_input_edit"].set_text(str(obj["vy"]))
    refresh_object_list(ui, sim)

def deselect_object(ui, sim):
    sim["ui_mode"] = ""
    sim["selected_object"] = None
    ui["ui_manager"].switch_page("right", "main")
    set_input_defaults(ui, DEFAULT_INPUTS)
    refresh_object_list(ui, sim)

def update_selected_object(ui, sim):
    obj = sim["selected_object"]
    if obj:
        obj["name"] = ui["name_input_edit"].get_text()
        try:
            obj["mass"] = max(1, int(ui["mass_input_edit"].get_text()))
        except ValueError:
            pass
        try:
            r = int(ui["radius_input_edit"].get_text())
            obj["radius"] = max(1, min(100, r))
            if r > 100:
                ui["radius_input_edit"].set_text("100")
        except ValueError:
            pass
        try:
            obj["vx"] = float(ui["vx_input_edit"].get_text())
        except Exception:
            pass
        try:
            obj["vy"] = float(ui["vy_input_edit"].get_text())
        except Exception:
            pass
        refresh_object_list(ui, sim)

def launch_confirm_delete_dialog(ui, sim):
    obj = sim["selected_object"]
    dialog = pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect((WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 75), (300, 150)),
        manager=ui["manager"],
        window_title='Confirm Deletion',
        action_long_desc=f"Are you sure you want to delete '{obj.get('name', obj['id'])}'?",
        action_short_name='Delete',
        blocking=True
    )
    dialog.object_to_delete = obj
    ui["confirm_dialog"] = dialog

def refresh_object_list(ui, sim):
    items = []
    for obj in sim["objects"]:
        label = f"{obj['id']}"
        if obj.get("name"):
            label += f" ({obj['name']})"
        items.append(label)
    ui["object_list"].set_item_list(items)
    sel = sim.get("selected_object")
    if sel:
        label = f"{sel['id']}"
        if sel.get("name"):
            label += f" ({sel['name']})"
        ui["object_list"].selected_item = label
    else:
        ui["object_list"].selected_item = None

def add_object(ui, sim):
    """Add a new object with properties from UI and a unique ID."""
    name = ui["name_input_add"].get_text()
    object_id_counter = sim["object_id_counter"]

    # Fallback default values
    if not name:
        name = DEFAULT_INPUTS["name"]
    try:
        mass = max(1, int(ui["mass_input_add"].get_text()))
    except Exception:
        mass = 10
    if not ui["mass_input_add"].get_text().strip():
        mass = 10
    try:
        radius = int(ui["radius_input_add"].get_text())
        if radius > 100:
            radius = 100
    except Exception:
        radius = 10
    if not ui["radius_input_add"].get_text().strip():
        radius = 10
    try:
        vx = float(ui["vx_input_add"].get_text())
    except Exception:
        vx = 0
    try:
        vy = float(ui["vy_input_add"].get_text())
    except Exception:
        vy = 0
    # Place in the center of simulation area
    x = (LEFT_SIDEBAR_WIDTH + (WINDOW_WIDTH - TOOLBAR_WIDTH)) // 2
    y = WINDOW_HEIGHT // 2
    shock_absorption = 0.001 * mass
    obj = {
        "id": object_id_counter,
        "name": name,
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy,
        "mass": mass,
        "radius": radius,
        "shock_absorption": shock_absorption,
        "color": (200, 50, 50),
    }
    object_id_counter += 1
    sim["objects"].append(obj)
    refresh_object_list(ui, sim)
    sim["selected_object"] = None

def set_input_defaults(ui, defaults=DEFAULT_INPUTS):
    ui["ui_manager"].switch_page("right", "main")
    ui["name_input_add"].set_text(str(defaults["name"]))
    ui["mass_input_add"].set_text(str(defaults["mass"]))
    ui["radius_input_add"].set_text(str(defaults["radius"]))
    ui["vx_input_add"].set_text("0")
    ui["vy_input_add"].set_text("0")