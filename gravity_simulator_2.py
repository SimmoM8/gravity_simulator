import pygame
import random
import pygame_gui
import numpy as np
from ui_manager import UIManager
from config import *
from ui_events import handle_event
from ui_actions import set_input_defaults




# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Vector Field Simulation")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 20)
header_font = pygame.font.SysFont(None, 28)

# Initialize UI manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
ui_manager = UIManager(manager)

# Initialize UI elements
field_display_mode = "vector"  # Default mode: 'vector' or 'heatmap'
objects = []

# Split state into ui and sim dictionaries
ui = {
    "manager": manager,
    "ui_manager": ui_manager,
    "object_list": ui_manager.get("object_list"),
    "menu_label": ui_manager.get("menu_label"),
    "name_input_add": ui_manager.get("name_input_add"),
    "mass_input_add": ui_manager.get("mass_input_add"),
    "radius_input_add": ui_manager.get("radius_input_add"),
    "vx_input_add": ui_manager.get("vx_input_add"),
    "vy_input_add": ui_manager.get("vy_input_add"),
    "name_input_edit": ui_manager.get("name_input_edit"),
    "mass_input_edit": ui_manager.get("mass_input_edit"),
    "radius_input_edit": ui_manager.get("radius_input_edit"),
    "vx_input_edit": ui_manager.get("vx_input_edit"),
    "vy_input_edit": ui_manager.get("vy_input_edit"),
    "field_toggle_button": ui_manager.get("field_toggle_button"),
    "pause_button": ui_manager.get("pause_button"),
    "reset_button": ui_manager.get("reset_button"),
    "toggle_trail_button": ui_manager.get("toggle_trail_button"),
    "trail_length_slider": ui_manager.get("trail_length_slider"),
    "toggle_velocity_vectors_button": ui_manager.get("toggle_velocity_vectors_button"), 
    "return_button_settings": ui_manager.get("return_button_settings"),
    "return_button_edit": ui_manager.get("return_button_edit"),
    "add_object_button": ui_manager.get("add_object_button"),
    "delete_object_button": ui_manager.get("delete_object_button"),
    "settings_button": ui_manager.get("settings_button"),
}

sim = {
    "objects": objects,
    "ui_mode": "",
    "selected_object": None,
    "dragging_object": None,
    "paused": False,
    "confirm_dialog": None,
    "field_display_mode": field_display_mode,
    "object_id_counter": 0,
    "trail_enabled": True,
    "trail_length": DEFAULT_INPUTS.get("trail_length", 50),
    "vectors_enabled": True,
}

set_input_defaults(ui, DEFAULT_INPUTS)

def draw_sidebar_background():
    """Draw the sidebar background."""
    # Left sidebar
    left_sidebar_rect = pygame.Rect(0, 0, LEFT_SIDEBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, (40, 40, 50), left_sidebar_rect)
    # Right sidebar
    sidebar_rect = pygame.Rect(WINDOW_WIDTH - TOOLBAR_WIDTH, 0, TOOLBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), sidebar_rect)  # Dark gray background

def draw_heatmap(X, Y, U, V):
    """Draw a heatmap using the color spectrum from blue (low) to red (high)."""
    magnitude = np.sqrt(U**2 + V**2)  # Compute the vector magnitudes
    max_magnitude = 1000000  # Maximum intensity
    min_magnitude = 0  # Minimum intensity

    # Normalize magnitudes to the range [0, 1]
    normalized_magnitude = (magnitude - min_magnitude) / (max_magnitude - min_magnitude)
    normalized_magnitude = np.clip(normalized_magnitude, 0, 1)  # Ensure values are clamped to [0, 1]

    # Iterate through the grid and draw each cell
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            intensity = normalized_magnitude[i, j]
            color = intensity_to_color(intensity)  # Map intensity to color

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
        if sim["trail_enabled"]:
            obj["trail"].append((obj["x"], obj["y"]))
            if len(obj["trail"]) > sim["trail_length"]:
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

        # Draw velocity vector with arrowhead
        if sim.get("vectors_enabled", True):
            vx, vy = obj["vx"], obj["vy"]
            speed = np.hypot(vx, vy)
            if speed > 0:
                scale = 10  # Adjust for visual size
                dx = int(vx / speed * scale * speed)
                dy = int(vy / speed * scale * speed)
                start_pos = (obj["x"], obj["y"])
                end_pos = (obj["x"] + dx, obj["y"] + dy)

                # Main vector line
                pygame.draw.line(screen, (0, 150, 255), start_pos, end_pos, 2)

                # Arrowhead
                angle = np.arctan2(dy, dx)
                arrow_size = 6
                left = (end_pos[0] - arrow_size * np.cos(angle - np.pi / 6),
                        end_pos[1] - arrow_size * np.sin(angle - np.pi / 6))
                right = (end_pos[0] - arrow_size * np.cos(angle + np.pi / 6),
                         end_pos[1] - arrow_size * np.sin(angle + np.pi / 6))
                pygame.draw.polygon(screen, (0, 150, 255), [end_pos, left, right])

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

# Main loop
running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0
    screen.fill(BACKGROUND_COLOR)

    # Draw sidebar background
    draw_sidebar_background()

    # Handle events via ui_events.handle_event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            handle_event(event, ui, sim)

    # Generate and draw the vector field
    X, Y, U, V = generate_vector_field(GRID_SIZE, objects)

    if field_display_mode == "vector":
        draw_vector_field(X, Y, U, V)
    elif field_display_mode == "heatmap":
        draw_heatmap(X, Y, U, V)

    if not sim["paused"]:
        update_object_velocities(U, V, X, Y)
        update_object_positions()

    # Draw objects
    draw_objects()

    # Draw top-center selected object display
    if sim["selected_object"]:
        selected_label = sim["selected_object"].get("name", str(sim["selected_object"]["id"]))
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
