import pygame
from core.vector_field import VectorField
from core.camera import Camera
import numpy as np
from setup.config import SIDEBAR_WIDTH, WINDOW_WIDTH, SIDEBAR_WIDTH, WINDOW_HEIGHT, GRID_SIZE, COEFFICIENT_OF_RESTITUTION, VECTOR_FIELD_COLOR, G, VELOCITY_VECTOR_COLOR

class Scene:
    def __init__(self):
        self.camera = Camera()
        self.objects = []
        self.field_mode = "vector"
        self.trail_enabled = True
        self.trail_length = 3 # Default trail length in seconds
        self.vectors_enabled = True
        self.object_id_counter = 0

        self.vector_field = VectorField(GRID_SIZE, self, self.camera)
        self._cached_positions = None
        self._cached_masses = None
        self.max_velocity = 0
        self.max_acceleration = 0

    def update(self, effective_time_delta):
        self.update_object_velocities(effective_time_delta)
        self.update_object_positions(effective_time_delta)

    def update_object_velocities(self, effective_time_delta):
        """Update velocities of objects based on gravitational forces."""

        # Cache object count
        n = len(self.objects)
        if n == 0:
            return

        # Cache object positions and masses
        self._cached_positions = np.array([[obj.x, obj.y] for obj in self.objects])
        self._cached_velocities = np.array([[obj.vx, obj.vy] for obj in self.objects])
        self._cached_masses = np.array([obj.mass for obj in self.objects])
        
        accelerations = np.zeros((n, 2)) # Initialize accelerations
        self.max_acceleration = 0
 
        for i in range(n):
            r_vectors = self._cached_positions - self._cached_positions[i]
            distances = np.linalg.norm(r_vectors, axis=1)

            # Clip distances to avoid extreme acceleration (at or below object radii)
            clipped_distances = np.maximum(
                distances,
                self.objects[i].radius + np.array([o.radius for o in self.objects])
            )

            mask = distances > 0  # exclude self-interaction

            strengths = np.zeros(n)
            strengths[mask] = G * self._cached_masses[mask] / (clipped_distances[mask] ** 2)

            directions = np.zeros_like(r_vectors)
            directions[mask] = r_vectors[mask] / distances[mask][:, np.newaxis]

            acceleration = (strengths[:, np.newaxis] * directions).sum(axis=0)
            accelerations[i] = acceleration
            self.max_acceleration = max(self.max_acceleration, np.linalg.norm(acceleration))

        new_velocities = self._cached_velocities + accelerations * effective_time_delta # Store new velocities
        self.max_velocity = np.max(np.linalg.norm(new_velocities, axis=1))

        # Update object velocities
        for i, obj in enumerate(self.objects):
            obj.vx, obj.vy = new_velocities[i]

    def update_object_positions(self, effective_time_delta):
        for i, obj in enumerate(self.objects):
            obj.x += obj.vx * effective_time_delta
            obj.y += obj.vy * effective_time_delta

            for j, other in enumerate(self.objects):
                if i != j:
                    dx = obj.x - other.x
                    dy = obj.y - other.y
                    distance = (dx**2 + dy**2)**0.5

                    # Check for collision
                    if distance <= (obj.radius + other.radius):
                        nx, ny = dx / distance, dy / distance # Normalize the normal vector
                        # Calculate relative velocity
                        dvx = obj.vx - other.vx
                        dvy = obj.vy - other.vy
                        relative_v = dvx * nx + dvy * ny
                        # If they are moving apart, skip collision response
                        if relative_v > 0:
                            continue
                        m1, m2 = obj.mass, other.mass
                        cor = COEFFICIENT_OF_RESTITUTION
                        impulse = -(1 + cor) * relative_v / (1/m1 + 1/m2) # Calculate elastic collision impulse
                        # Update velocities based on impulse
                        obj.vx += (impulse * nx) / m1
                        obj.vy += (impulse * ny) / m1
                        other.vx -= (impulse * nx) / m2
                        other.vy -= (impulse * ny) / m2
                        # Adjust positions to prevent overlap and ensure they are separated
                        overlap = obj.radius + other.radius - distance 
                        correction_x = nx * overlap / 2
                        correction_y = ny * overlap / 2
                        obj.x += correction_x
                        obj.y += correction_y
                        other.x -= correction_x
                        other.y -= correction_y

    def draw(self, surface, font, sim):
        # Draw vector or heatmap field
        SX, SY, U, V = self.vector_field.generate()
        if self.field_mode == "vector":
            self.draw_vector_field(surface, SX, SY, U, V)
        elif self.field_mode == "heatmap":
            self.draw_heatmap(surface, SX, SY, U, V)

        # Draw objects with trails
        self.draw_objects(surface, font, sim)

        # Draw scale bar overlay
        self.draw_scale_bar(surface, self.camera, font)

    def draw_vector_field(self, surface, SX, SY, U, V):
        # Implement vector drawing using camera.world_to_screen for positions
        max_arrow_length = GRID_SIZE

        magnitude = (U**2 + V**2)**0.5 # Calculate magnitude of vectors using pythagorean theorem
        max_magnitude = magnitude.max() if magnitude.size > 0 else 1

        scaled_magnitude = np.log1p(magnitude) / np.log1p(max_magnitude + 1e-10) * max_arrow_length

        for i in range(SX.shape[0]):
            for j in range(SX.shape[1]):
                grid_point_start = (SX[i,j], SY[i,j])
                mag = magnitude[i,j]
                if mag == 0:
                    pygame.draw.circle(surface, VECTOR_FIELD_COLOR, (int(grid_point_start[0]), int(grid_point_start[1])), 1)
                    continue

                arrow_length = scaled_magnitude[i,j]
                dx = U[i,j] / mag * arrow_length
                dy = V[i,j] / mag * arrow_length

                grid_point_end = (
                    grid_point_start[0] + dx,
                    grid_point_start[1] + dy,
                )
                pygame.draw.line(surface, VECTOR_FIELD_COLOR,
                                 (int(grid_point_start[0]), int(grid_point_start[1])),
                                 (int(grid_point_end[0]), int(grid_point_end[1])), 1)
                pygame.draw.circle(surface, VECTOR_FIELD_COLOR,
                                   (int(grid_point_end[0]), int(grid_point_end[1])), 1)

    def draw_heatmap(self, surface, X, Y, U, V):
        # Implement your heatmap drawing here, using camera.world_to_screen for position
        pass

    def draw_objects(self, surface, font, sim):
        visible_objects = [
            obj for obj in self.objects
            if 0 <= self.camera.world_to_screen(obj.x, obj.y)[0] <= surface.get_width()
            and 0 <= self.camera.world_to_screen(obj.x, obj.y)[1] <= surface.get_height()
        ]

        # Create transparent surface for fading trails
        trail_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        max_visible_speed = max(
            (obj.vx**2 + obj.vy**2)**0.5 for obj in visible_objects
        ) if visible_objects else 1

        for obj in self.objects:
            # Draw trails
            if self.trail_enabled:
                if not hasattr(obj, "trail"):
                    obj.trail = []

                # Append current position and elapsed time to trail
                obj.trail.append((obj.x, obj.y, sim.elapsed_time))

                trimmed_trail = []
                max_length = 1e30 # Limit trail length to 100 million meters
                max_age = self.trail_length * sim.speed_multiplier # Limit trail age to 3 seconds
                total_length = 0.0 # Initialize total length of the trail
                last_x, last_y = obj.x, obj.y # Initialize last position with current position

                # Trim trail to max length and age
                for tx, ty, t_time in reversed(obj.trail):
                    age = sim.elapsed_time - t_time # Calculate age of the trail segment

                    # Calculate distance from last position
                    dx = last_x - tx 
                    dy = last_y - ty
                    segment_length = (dx**2 + dy**2)**0.5
                    total_length += segment_length # Update total trail length
                    # If the segment is within the limits, keep it
                    if age <= max_age and total_length <= max_length:
                        trimmed_trail.insert(0, (tx, ty, t_time)) # Append to the front of the trail
                        last_x, last_y = tx, ty
                    else:
                        break

                obj.trail = trimmed_trail
            else:
                obj.trail = []

            # Draw trail
            if len(obj.trail) > 1:
                for i in range(1, len(obj.trail)):
                    start_pos = self.camera.world_to_screen(obj.trail[i - 1][0], obj.trail[i - 1][1])
                    end_pos = self.camera.world_to_screen(obj.trail[i][0], obj.trail[i][1])
                    alpha = int(255 * i / len(obj.trail))
                    color = (*obj.color, alpha)
                    pygame.draw.line(trail_surface, color, start_pos, end_pos, 2)

            # Draw object circle
            sx, sy = self.camera.world_to_screen(obj.x, obj.y)
            screen_radius = max(1, int(obj.radius * self.camera.pixels_per_meter))
            pygame.draw.circle(surface, obj.color, (sx, sy), screen_radius)

            # Draw label
            label = f"{obj.id}"
            if getattr(obj, "name", None):
                label += f" ({obj.name})"
            label_surf = font.render(label, True, (255,255,255))
            surface.blit(label_surf, (sx + screen_radius + 5, sy - 10))

            # Draw velocity vector if enabled
            if self.vectors_enabled:
                speed = (obj.vx**2 + obj.vy**2)**0.5
                if speed > 0:

                    distance_m = speed * sim.speed_multiplier * 0.8

                    length_pixels = distance_m * self.camera.pixels_per_meter

                    length_pixels = min(150, length_pixels) # Limit max vector length

                    vx_unit = obj.vx / speed
                    vy_unit = obj.vy / speed

                    vx_screen = vx_unit * length_pixels
                    vy_screen = vy_unit * length_pixels

                    start = sx, sy  # object's screen position
                    end = sx + vx_screen, sy + vy_screen

                    pygame.draw.line(surface, VELOCITY_VECTOR_COLOR, start, end, 2)
                    pygame.draw.circle(surface, VELOCITY_VECTOR_COLOR, (int(end[0]), int(end[1])), 2)

        # Blit trail surface on top of main surface
        surface.blit(trail_surface, (0, 0))

    def draw_scale_bar(self, surface, camera, font):
        bar_width = 200
        margin = 20
        bar_height = 8
        num_ticks = 10
        tick_height = 6
        tick_color = (200, 200, 200)
        text_color = (230, 230, 230)

        pixels_per_meter = camera.pixels_per_meter
        scale_meters = bar_width / pixels_per_meter

        # Determine unit and scale label text
        if scale_meters >= 1.5e11:  # approx 1 AU in meters
            scale_au = scale_meters / 1.496e11
            label_text = f"{scale_au:.2f} AU"
            unit_scale = 1.496e11
        elif scale_meters >= 1000:
            scale_km = scale_meters / 1000
            label_text = f"{scale_km:.2f} km"
            unit_scale = 1000
        else:
            label_text = f"{scale_meters:.2f} m"
            unit_scale = 1

        # Position bottom right (adjust for toolbar width if needed)
        x = surface.get_width() - bar_width - margin - SIDEBAR_WIDTH
        y = surface.get_height() - margin - bar_height - 50  # 50 includes text height and spacing

        # Draw scale bar
        pygame.draw.rect(surface, (230, 230, 230), (x, y, bar_width + 2, bar_height))

        # Draw label above bar
        label_surface = font.render(label_text, True, text_color)
        surface.blit(label_surface, (x, y - 18))

        x += 1 # Adjust tick position to align with bar

        # Draw ticks and tick labels
        for i in range(num_ticks):
            tick_x = x + int(i * (bar_width / (num_ticks - 1)) -1)
            tick_top = y + bar_height
            tick_bottom = tick_top + tick_height

            # Draw tick line
            pygame.draw.line(surface, tick_color, (tick_x, tick_top), (tick_x, tick_bottom), 2)
