import pygame
import random
import pygame_gui
import numpy as np
from ui_manager import UIManager
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_WIDTH, LEFT_SIDEBAR_WIDTH,
    BACKGROUND_COLOR, VECTOR_FIELD_COLOR, FPS, GRID_SIZE,
    TRAIL_DEFAULT_LENGTH
)


# Trail settings
show_trails = True
trail_max_length = TRAIL_DEFAULT_LENGTH

# Initialize Pygame
pygame.init()


screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Vector Field Simulation")
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
ui_manager = UIManager(manager)
ui_manager.debug_print_panels()  # Print panel structure for debugging

font = pygame.font.SysFont(None, 20)
# Font for top-center header
header_font = pygame.font.SysFont(None, 28)

# Track current field display mode
field_display_mode = "vector"  # Default mode: 'vector' or 'heatmap'

confirm_dialog = None

ui_mode = 'add'  # 'add' or 'edit'

object_list = ui_manager.get("object_list")
menu_label = ui_manager.get("menu_label")
name_label = ui_manager.get("name_label")
name_input = ui_manager.get("name_input")
mass_label = ui_manager.get("mass_label")
mass_input = ui_manager.get("mass_input")
radius_label = ui_manager.get("radius_label")
radius_input = ui_manager.get("radius_input")
field_toggle_button = ui_manager.get("field_toggle_button")
pause_button = ui_manager.get("pause_button")
reset_button = ui_manager.get("reset_button")
trail_toggle_button = ui_manager.get("trail_toggle_button")
trail_length_slider = ui_manager.get("trail_length_slider")
return_button = ui_manager.get("return_button")
add_object_button = ui_manager.get("add_object_button")
delete_object_button = ui_manager.get("delete_object_button")
settings_button = ui_manager.get("settings_button")

objects = []

# Global object ID counter
object_id_counter = 0

# Helper function to generate a unique name
def get_unique_name(base_id):
    base_name = str(base_id)
    existing_names = {obj.get("name", str(obj["id"])) for obj in objects}
    if base_name not in existing_names:
        return base_name
    counter = 1
    while f"{base_name}_{counter}" in existing_names:
        counter += 1
    return f"{base_name}_{counter}"

# Set initial default values for inputs
name_input.set_text(get_unique_name(object_id_counter))
mass_input.set_text("10")
radius_input.set_text("10")

def draw_sidebar_background():
    """Draw the sidebar background."""
    # Left sidebar
    left_sidebar_rect = pygame.Rect(0, 0, LEFT_SIDEBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, (40, 40, 50), left_sidebar_rect)
    # Right sidebar
    sidebar_rect = pygame.Rect(WINDOW_WIDTH - TOOLBAR_WIDTH, 0, TOOLBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), sidebar_rect)  # Dark gray background

# Objects List
selected_object = None
dragging_object = None  # Track the object being dragged

# Functions
def draw_heatmap(X, Y, U, V):
    """Draw a heatmap using the color spectrum from blue (low) to red (high)."""
    magnitude = np.sqrt(U**2 + V**2)  # Compute the vector magnitudes
    max_magnitude = 1000000  # Maximum intensity
    min_magnitude = 0  # Minimum intensity

    # Normalize magnitudes to the range [0, 1]
    normalized_magnitude = (magnitude - min_magnitude) / (max_magnitude - min_magnitude)
    normalized_magnitude = np.clip(normalized_magnitude, 0, 1)  # Ensure values are clamped to [0, 1]
    print(normalized_magnitude)

    # Iterate through the grid and draw each cell
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            intensity = normalized_magnitude[i, j]
            print(intensity)
            color = intensity_to_color(intensity)  # Map intensity to color
            print(color)

            # Draw the cell
            rect = pygame.Rect(int(X[i, j]), int(Y[i, j]), GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, color, rect)


def intensity_to_color(intensity):
    """Convert normalized intensity (0 to 1) to ROYGBIV spectrum."""
    # Map intensity to a position in the spectrum
    if intensity <= 0.166:  # Red to Orange
        ratio = intensity / 0.166
        r = 255
        g = int(255 * ratio)
        b = 0
    elif intensity <= 0.333:  # Orange to Yellow
        ratio = (intensity - 0.166) / 0.166
        r = 255
        g = 255
        b = int(255 * ratio)
    elif intensity <= 0.5:  # Yellow to Green
        ratio = (intensity - 0.333) / 0.167
        r = int(255 * (1 - ratio))
        g = 255
        b = 0
    elif intensity <= 0.666:  # Green to Blue
        ratio = (intensity - 0.5) / 0.166
        r = 0
        g = int(255 * (1 - ratio))
        b = int(255 * ratio)
    elif intensity <= 0.833:  # Blue to Indigo
        ratio = (intensity - 0.666) / 0.166
        r = int(75 * ratio)
        g = 0
        b = 255
    else:  # Indigo to Violet
        ratio = (intensity - 0.833) / 0.167
        r = int(238 * ratio + 75)
        g = 0
        b = int(255 * (1 - ratio))

    return (r, g, b)



def draw_objects():
    """Draw objects as circles with trails and ID labels."""
    # Update trails for each object
    for obj in objects:
        if "trail" not in obj:
            obj["trail"] = []
        if show_trails:
            obj["trail"].append((obj["x"], obj["y"]))
            if len(obj["trail"]) > trail_max_length:
                obj["trail"].pop(0)
        else:
            obj["trail"] = []
    # Draw trails and objects
    for obj in objects:
        trail_length = len(obj["trail"])
        for i, point in enumerate(obj["trail"]):
            fade = int(255 * (i / trail_length)) if trail_length > 0 else 255  # older = dimmer
            color = (*obj["color"][:3], fade)
            trail_surface = pygame.Surface((2, 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, color, (1, 1), 1)
            screen.blit(trail_surface, (int(point[0]), int(point[1])))
        pygame.draw.circle(screen, obj["color"], (obj["x"], obj["y"]), int(obj["radius"]))
        # Draw ID label and name
        label_str = f"{obj['id']}"
        if obj.get("name"):
            label_str += f" ({obj['name']})"
        label = font.render(label_str, True, (255, 255, 255))
        label_pos = (obj["x"] + int(obj["radius"]) + 5, obj["y"] - 10)
        screen.blit(label, label_pos)

def select_object(obj):
    global selected_object
    selected_object = obj
    ui_manager.switch_page("right", "edit")
    # Update sidebar inputs with the selected object's properties
    name_input.set_text(str(selected_object.get("name", "")))
    mass_input.set_text(str(selected_object["mass"]))
    radius_input.set_text(str(int(selected_object["radius"])))
    menu_label.set_text(f"✏️ Edit Object {obj['id']}")

def update_selected_object():
    """Update the properties of the selected object based on input fields."""
    global selected_object
    if selected_object:
        # Update name
        selected_object["name"] = name_input.get_text()
        # Update mass
        try:
            selected_object["mass"] = max(1, int(mass_input.get_text()))
        except ValueError:
            pass  # Ignore invalid input
        # Update radius with max limit
        try:
            radius = int(radius_input.get_text())
            if radius > 100:
                radius = 100
                radius_input.set_text("100")
            selected_object["radius"] = max(1, radius)
        except ValueError:
            pass  # Ignore invalid input
        refresh_object_list()

def handle_mouse_click(mouse_pos):
    """Handle mouse click to select or start dragging an object."""
    global selected_object, dragging_object, ui_mode
    # Only allow clicking in the simulation area (not left or right sidebar)
    sim_left = LEFT_SIDEBAR_WIDTH
    sim_right = WINDOW_WIDTH - TOOLBAR_WIDTH
    x, y = mouse_pos
    if not (sim_left <= x < sim_right and 0 <= y < WINDOW_HEIGHT):
        return
    for obj in objects:
        dist = ((mouse_pos[0] - obj["x"])**2 + (mouse_pos[1] - obj["y"])**2)**0.5
        if dist < obj["radius"]:  # Object clicked
            dragging_object = obj  # Start dragging
            select_object(obj)
            return
    # No object was clicked, reset selection and switch to add mode
    selected_object = None
    ui_mode = 'add'
    name_input.set_text(get_unique_name(object_id_counter))
    mass_input.set_text("10")
    radius_input.set_text("10")
    menu_label.set_text("➕ Add New Object")
    refresh_object_list()
    ui_manager.switch_page("right", "main")  # Switch to home page

def handle_mouse_release():
    """Stop dragging an object."""
    global dragging_object
    dragging_object = None

def handle_mouse_drag(mouse_pos):
    """Move the object being dragged."""
    global dragging_object
    if dragging_object:
        # Restrict to simulation area
        min_x = LEFT_SIDEBAR_WIDTH + dragging_object["radius"]
        max_x = WINDOW_WIDTH - TOOLBAR_WIDTH - dragging_object["radius"]
        min_y = dragging_object["radius"]
        max_y = WINDOW_HEIGHT - dragging_object["radius"]
        dragging_object["x"] = max(min_x, min(max_x, mouse_pos[0]))
        dragging_object["y"] = max(min_y, min(max_y, mouse_pos[1]))

def draw_vector_field(X, Y, U, V):
    """Draw a vector field as arrows or dots if magnitude is 0."""
    magnitude = np.sqrt(U**2 + V**2)
    scaled_magnitude = np.log1p(magnitude) * 5000
    max_arrow_length = GRID_SIZE // 2

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            # If magnitude is 0, draw a dot
            if magnitude[i, j] == 0:
                pygame.draw.circle(screen, VECTOR_FIELD_COLOR, (int(X[i, j]), int(Y[i, j])), 2)
                continue

            # Calculate arrow length and direction
            arrow_length = min(max_arrow_length, int(scaled_magnitude[i, j]))
            dx = int(U[i, j] / magnitude[i, j] * arrow_length) if magnitude[i, j] > 0 else 0
            dy = int(V[i, j] / magnitude[i, j] * arrow_length) if magnitude[i, j] > 0 else 0

            start = (int(X[i, j]), int(Y[i, j]))
            end = (start[0] + dx, start[1] + dy)

            pygame.draw.line(screen, VECTOR_FIELD_COLOR, start, end, 1)
            pygame.draw.circle(screen, VECTOR_FIELD_COLOR, end, 2)  # Arrowhead as a dot

def add_object():
    """Add a new object with properties from UI and a unique ID."""
    global object_id_counter, ui_mode, selected_object
    # Fallback default values
    name = name_input.get_text()
    if not name:
        name = get_unique_name(object_id_counter)
    # Validate uniqueness of name
    existing_names = {obj.get("name", str(obj["id"])) for obj in objects}
    if name in existing_names:
        print("Duplicate name detected. Please choose a different name.")
        return
    try:
        mass = max(1, int(mass_input.get_text()))
    except Exception:
        mass = 10
    if not mass_input.get_text().strip():
        mass = 10
    try:
        radius = int(radius_input.get_text())
        if radius > 100:
            radius = 100
    except Exception:
        radius = 10
    if not radius_input.get_text().strip():
        radius = 10
    # Place in the center of simulation area
    x = (LEFT_SIDEBAR_WIDTH + (WINDOW_WIDTH - TOOLBAR_WIDTH)) // 2
    y = WINDOW_HEIGHT // 2
    shock_absorption = 0.001 * mass
    obj = {
        "id": object_id_counter,
        "x": x,
        "y": y,
        "vx": 0,
        "vy": 0,
        "mass": mass,
        "radius": radius,
        "shock_absorption": shock_absorption,
        "color": (200, 50, 50),
        "name": name,
    }
    object_id_counter += 1
    objects.append(obj)
    refresh_object_list()
    # Reset inputs to new defaults after incrementing object_id_counter
    name_input.set_text(get_unique_name(object_id_counter))
    mass_input.set_text("10")
    radius_input.set_text("10")
    selected_object = None
    ui_mode = 'add'
    # Update menu label to add mode
    menu_label.set_text("➕ Add New Object")
def refresh_object_list():
    """Refresh the object list in the left sidebar."""
    items = []
    for obj in objects:
        label = f"{obj['id']}"
        if obj.get("name"):
            label += f" ({obj['name']})"
        items.append(label)
    object_list.set_item_list(items)
    # Highlight selected object if present
    if selected_object:
        sel_label = f"{selected_object['id']}"
        if selected_object.get("name"):
            sel_label += f" ({selected_object['name']})"
        object_list.selected_item = sel_label
    else:
        object_list.selected_item = None


def generate_vector_field(grid_size, objects):
    """Generate a vector field based on objects' positions and masses."""
    x = np.arange(0, WINDOW_WIDTH, grid_size)
    y = np.arange(0, WINDOW_HEIGHT, grid_size)
    X, Y = np.meshgrid(x, y)

    # Initialize field components
    U = np.zeros_like(X, dtype=float)
    V = np.zeros_like(Y, dtype=float)

    # Add contributions from each object
    for obj in objects:
        dx = X - obj["x"]
        dy = Y - obj["y"]
        distance = np.sqrt(dx**2 + dy**2)
        distance[distance == 0] = 0.1  # Avoid division by zero
        flow_strength = obj["mass"] / distance**2
        U -= flow_strength * dx / distance
        V -= flow_strength * dy / distance

    return X, Y, U, V

def update_object_velocities(U, V, X, Y):
    """Update object velocities based on the vector field, ignoring self-contribution."""
    for obj in objects:
        # Find the nearest grid point to the object
        gx = int(obj["x"] // GRID_SIZE)
        gy = int(obj["y"] // GRID_SIZE)

        if 0 <= gx < U.shape[1] and 0 <= gy < U.shape[0]:
            # Calculate the field excluding the object's self-contribution
            local_U, local_V = 0, 0
            for other in objects:
                if other is obj:  # Skip self-contribution
                    continue

                dx = obj["x"] - other["x"]
                dy = obj["y"] - other["y"]
                distance = np.sqrt(dx**2 + dy**2)
                if distance > 0:  # Ignore direct overlap
                    strength = other["mass"] / distance**2
                    local_U -= strength * dx / distance
                    local_V -= strength * dy / distance

            # Update velocity
            obj["vx"] += local_U * 0.1  # Scale for smoother motion
            obj["vy"] += local_V * 0.1

def update_object_positions():
    """Update object positions based on their velocities and handle collisions."""
    for i, obj in enumerate(objects):
        # Update position based on velocity
        obj["x"] += obj["vx"]
        obj["y"] += obj["vy"]

        # Boundary collision
        if obj["x"] - obj["radius"] < 0 or obj["x"] + obj["radius"] > WINDOW_WIDTH - TOOLBAR_WIDTH:
            obj["vx"] *= -1  # Reverse velocity
            obj["vx"] *= (1 - obj["shock_absorption"])  # Apply shock absorption
            obj["x"] = max(obj["radius"], min(WINDOW_WIDTH - TOOLBAR_WIDTH - obj["radius"], obj["x"]))

        if obj["y"] - obj["radius"] < 0 or obj["y"] + obj["radius"] > WINDOW_HEIGHT:
            obj["vy"] *= -1  # Reverse velocity
            obj["vy"] *= (1 - obj["shock_absorption"])  # Apply shock absorption
            obj["y"] = max(obj["radius"], min(WINDOW_HEIGHT - obj["radius"], obj["y"]))

        # Object-object collision
        for j, other in enumerate(objects):
            if i != j:
                dx = obj["x"] - other["x"]
                dy = obj["y"] - other["y"]
                distance = np.sqrt(dx**2 + dy**2)

                # Check for collision
                if distance < obj["radius"] + other["radius"]:
                    # Normal vector
                    nx, ny = dx / distance, dy / distance

                    # Relative velocity
                    dvx = obj["vx"] - other["vx"]
                    dvy = obj["vy"] - other["vy"]

                    # Velocity along the normal
                    v_rel = dvx * nx + dvy * ny

                    # Ignore objects moving apart
                    if v_rel > 0:
                        continue

                    # Combined mass
                    combined_mass = obj["mass"] + other["mass"]

                    # Shock absorption effects
                    obj_absorb = obj["shock_absorption"]
                    other_absorb = other["shock_absorption"]
                    energy_loss = (obj_absorb + other_absorb) / 2

                    # Impulse scalar
                    impulse = -(1 - energy_loss) * v_rel / (1 / obj["mass"] + 1 / other["mass"])

                    # Apply impulse
                    obj["vx"] += (impulse * nx) / obj["mass"]
                    obj["vy"] += (impulse * ny) / obj["mass"]
                    other["vx"] -= (impulse * nx) / other["mass"]
                    other["vy"] -= (impulse * ny) / other["mass"]

                    # Separate objects to avoid overlap
                    overlap = obj["radius"] + other["radius"] - distance
                    obj["x"] += nx * overlap * (other["mass"] / combined_mass)
                    obj["y"] += ny * overlap * (other["mass"] / combined_mass)
                    other["x"] -= nx * overlap * (obj["mass"] / combined_mass)
                    other["y"] -= ny * overlap * (obj["mass"] / combined_mass)

paused = False

# Main loop
running = True
refresh_object_list()
ui_manager.switch_page("right", "main")  # Start with the home page
while running:
    time_delta = clock.tick(FPS) / 1000.0
    screen.fill(BACKGROUND_COLOR)

    # Draw sidebar background
    draw_sidebar_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle mouse interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                handle_mouse_click(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left button released
                handle_mouse_release()
        elif event.type == pygame.MOUSEMOTION:
            if dragging_object:
                handle_mouse_drag(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                if selected_object:
                    confirm_dialog = pygame_gui.windows.UIConfirmationDialog(
                        rect=pygame.Rect((WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 75), (300, 150)),
                        manager=manager,
                        window_title='Confirm Deletion',
                        action_long_desc=f"Are you sure you want to delete '{selected_object.get('name', selected_object['id'])}'?",
                        action_short_name='Delete',
                        blocking=True
                    )
                    confirm_dialog.object_to_delete = selected_object

        # Handle sidebar and GUI events
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                # Only update object if in edit mode
                if ui_mode == 'edit':
                    update_selected_object()
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == add_object_button:
                    # Only add if in add mode
                    if ui_mode == 'add':
                        add_object()
                elif event.ui_element == delete_object_button and selected_object:
                    confirm_dialog = pygame_gui.windows.UIConfirmationDialog(
                        rect=pygame.Rect((WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 75), (300, 150)),
                        manager=manager,
                        window_title='Confirm Deletion',
                        action_long_desc=f"Are you sure you want to delete '{selected_object.get('name', selected_object['id'])}'?",
                        action_short_name='Delete',
                        blocking=True
                    )
                    confirm_dialog.object_to_delete = selected_object
                elif confirm_dialog and event.ui_element == confirm_dialog.confirm_button:
                    # Delete the object associated with this confirmation
                    obj_to_delete = confirm_dialog.object_to_delete if hasattr(confirm_dialog, "object_to_delete") else None
                    if obj_to_delete and obj_to_delete in objects:
                        objects.remove(obj_to_delete)
                        if selected_object == obj_to_delete:
                            selected_object = None
                            ui_mode = 'add'
                            name_input.set_text(get_unique_name(object_id_counter))
                            mass_input.set_text("10")
                            radius_input.set_text("10")
                            menu_label.set_text("➕ Add New Object")
                            add_object_button.show()
                        refresh_object_list()
                    confirm_dialog.kill()
                    confirm_dialog = None
                elif confirm_dialog and event.ui_element == confirm_dialog.cancel_button:
                    confirm_dialog.kill()
                    confirm_dialog = None
                elif event.ui_element == field_toggle_button:
                    # Toggle field display mode
                    if field_display_mode == "vector":
                        field_display_mode = "heatmap"
                        field_toggle_button.set_text("Switch to Vectors")
                    else:
                        field_display_mode = "vector"
                        field_toggle_button.set_text("Switch to Heatmap")
                elif event.ui_element == pause_button:
                    paused = not paused
                    pause_button.set_text('Resume' if paused else 'Pause')
                elif event.ui_element == reset_button:
                    objects.clear()
                    selected_object = None
                    ui_mode = 'add'
                    name_input.set_text(get_unique_name(object_id_counter))
                    mass_input.set_text("10")
                    radius_input.set_text("10")
                    menu_label.set_text("➕ Add New Object")
                    refresh_object_list()
                    add_object_button.show()
                    # Switch to home page on reset
                    ui_manager.switch_page("right", "main")
                elif event.ui_element == trail_toggle_button:
                    show_trails = not show_trails
                    trail_toggle_button.set_text('Show Trails' if not show_trails else 'Hide Trails')
                elif event.ui_element == trail_length_slider:
                    trail_max_length = int(trail_length_slider.get_current_value())
                elif event.ui_element == return_button:
                    ui_manager.switch_page("right", "main")
                elif event.ui_element == settings_button:
                    ui_manager.switch_page("right", "settings")
            if event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                # Handle object selection from the object list
                selected_label = event.text
                # Find the object whose label matches
                found = None
                for obj in objects:
                    label = f"{obj['id']}"
                    if obj.get("name"):
                        label += f" ({obj['name']})"
                    if label == selected_label:
                        found = obj
                        break
                if found:
                    select_object(found)
                else:
                    selected_object = None
                    ui_mode = 'add'
                    name_input.set_text(get_unique_name(object_id_counter))
                    mass_input.set_text("10")
                    radius_input.set_text("10")
                    menu_label.set_text("➕ Add New Object")
                    add_object_button.show()
                refresh_object_list()
            if event.user_type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION:
                #Unselect: switch to add mode
                selected_object = None
                ui_mode = 'add'
                name_input.set_text(get_unique_name(object_id_counter))
                mass_input.set_text("10")
                radius_input.set_text("10")
                menu_label.set_text("➕ Add New Object")
                refresh_object_list()
                add_object_button.show()

        manager.process_events(event)

    # Generate and draw the vector field
    X, Y, U, V = generate_vector_field(GRID_SIZE, objects)

    if field_display_mode == "vector":
        draw_vector_field(X, Y, U, V)
    elif field_display_mode == "heatmap":
        draw_heatmap(X, Y, U, V)

    if not paused:
        update_object_velocities(U, V, X, Y)
        update_object_positions()

    # Draw objects
    draw_objects()

    # Draw top-center selected object display
    if selected_object:
        selected_label = selected_object.get("name", str(selected_object["id"]))
    else:
        selected_label = "None"
    header_text = header_font.render(f"Selected: {selected_label}", True, (255, 255, 255))
    # Compute center of simulation area (excluding sidebars)
    sim_width = WINDOW_WIDTH - TOOLBAR_WIDTH - LEFT_SIDEBAR_WIDTH
    sim_x = LEFT_SIDEBAR_WIDTH
    header_x = sim_x + (sim_width // 2) - (header_text.get_width() // 2)
    screen.blit(header_text, (header_x, 10))

    manager.update(time_delta)
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()
