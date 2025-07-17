import pygame
import random
import pygame_gui
import numpy as np

# Constants
WIDTH, HEIGHT = 800, 600
TOOLBAR_WIDTH = 200
BACKGROUND_COLOR = (30, 30, 30)
VECTOR_FIELD_COLOR = (100, 200, 100)
FPS = 60
GRID_SIZE = 20

# Initialize Pygame
pygame.init()

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vector Field Simulation")
clock = pygame.time.Clock()

# Track current field display mode
field_display_mode = "vector"  # Default mode: 'vector' or 'heatmap'


# Pygame GUI setup
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# UI Elements
add_object_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 20), (TOOLBAR_WIDTH - 40, 40)),
    text='Add Object',
    manager=manager
)

mass_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 80), (TOOLBAR_WIDTH - 40, 30)),
    text="Mass:",
    manager=manager
)
mass_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 110), (TOOLBAR_WIDTH - 40, 30)),
    manager=manager
)

radius_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 150), (TOOLBAR_WIDTH - 40, 30)),
    text="Radius:",
    manager=manager
)
radius_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 180), (TOOLBAR_WIDTH - 40, 30)),
    manager=manager
)
# Add a toggle button for field display mode
field_toggle_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 220), (TOOLBAR_WIDTH - 40, 40)),
    text='Switch to Heatmap',
    manager=manager
)

pause_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 280), (TOOLBAR_WIDTH - 40, 40)),
    text='Pause',
    manager=manager
)
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - TOOLBAR_WIDTH + 20, 340), (TOOLBAR_WIDTH - 40, 40)),
    text='Reset',
    manager=manager
)

def draw_sidebar_background():
    """Draw the sidebar background."""
    sidebar_rect = pygame.Rect(WIDTH - TOOLBAR_WIDTH, 0, TOOLBAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), sidebar_rect)  # Dark gray background

# Objects List
objects = []
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
    """Draw objects as circles."""
    for obj in objects:
        pygame.draw.circle(screen, obj["color"], (obj["x"], obj["y"]), obj["radius"])

def select_object(obj):
    """Select an object and update sidebar inputs."""
    global selected_object
    selected_object = obj
    # Update sidebar inputs with the selected object's properties
    mass_input.set_text(str(selected_object["mass"]))
    radius_input.set_text(str(selected_object["radius"]))

def update_selected_object():
    """Update the properties of the selected object based on input fields."""
    global selected_object
    if selected_object:
        # Update mass
        try:
            selected_object["mass"] = max(1, int(mass_input.get_text()))
        except ValueError:
            pass  # Ignore invalid input

        # Update radius with max limit
        try:
            radius = int(radius_input.get_text())
            if radius > 100:  # Limit radius to 10
                radius = 100
                radius_input.set_text("100")
            selected_object["radius"] = max(1, radius)
        except ValueError:
            pass  # Ignore invalid input

def handle_mouse_click(mouse_pos):
    """Handle mouse click to select or start dragging an object."""
    global selected_object, dragging_object
    for obj in objects:
        dist = ((mouse_pos[0] - obj["x"])**2 + (mouse_pos[1] - obj["y"])**2)**0.5
        if dist < obj["radius"]:  # Object clicked
            dragging_object = obj  # Start dragging
            select_object(obj)
            return

def handle_mouse_release():
    """Stop dragging an object."""
    global dragging_object
    dragging_object = None

def handle_mouse_drag(mouse_pos):
    """Move the object being dragged."""
    global dragging_object
    if dragging_object:
        dragging_object["x"] = max(dragging_object["radius"], min(WIDTH - TOOLBAR_WIDTH - dragging_object["radius"], mouse_pos[0]))
        dragging_object["y"] = max(dragging_object["radius"], min(HEIGHT - dragging_object["radius"], mouse_pos[1]))

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
    """Add a new object with random properties."""
    x = random.randint(50, WIDTH - TOOLBAR_WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    mass = random.randint(10, 1000)  # Random mass
    shock_absorption = 0.001 * mass  # Proportional to mass
    obj = {
        "x": x,
        "y": y,
        "vx": 0,  # Initial x velocity
        "vy": 0,  # Initial y velocity
        "mass": mass,
        "radius": mass/50,
        "shock_absorption": shock_absorption,  # Calculated absorption
        "color": (200, 50, 50),
    }
    objects.append(obj)


def generate_vector_field(grid_size, objects):
    """Generate a vector field based on objects' positions and masses."""
    x = np.arange(0, WIDTH, grid_size)
    y = np.arange(0, HEIGHT, grid_size)
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
        if obj["x"] - obj["radius"] < 0 or obj["x"] + obj["radius"] > WIDTH - TOOLBAR_WIDTH:
            obj["vx"] *= -1  # Reverse velocity
            obj["vx"] *= (1 - obj["shock_absorption"])  # Apply shock absorption
            obj["x"] = max(obj["radius"], min(WIDTH - TOOLBAR_WIDTH - obj["radius"], obj["x"]))

        if obj["y"] - obj["radius"] < 0 or obj["y"] + obj["radius"] > HEIGHT:
            obj["vy"] *= -1  # Reverse velocity
            obj["vy"] *= (1 - obj["shock_absorption"])  # Apply shock absorption
            obj["y"] = max(obj["radius"], min(HEIGHT - obj["radius"], obj["y"]))

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
                if event.pos[0] < WIDTH - TOOLBAR_WIDTH:  # Click in simulation area
                    handle_mouse_click(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left button released
                handle_mouse_release()
        elif event.type == pygame.MOUSEMOTION:
            if dragging_object:
                handle_mouse_drag(event.pos)

        # Handle sidebar events
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                update_selected_object()
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == add_object_button:
                    add_object()
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
    manager.update(time_delta)
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()
