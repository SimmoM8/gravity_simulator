import numpy as np
from setup.config import G, SIDEBAR_WIDTH, WINDOW_WIDTH, SIDEBAR_WIDTH, WINDOW_HEIGHT, GRID_SIZE

class VectorField:
    def __init__(self, grid_spacing_px, scene, camera):
        self.grid_spacing_px = grid_spacing_px
        self.scene = scene
        self.camera = camera

    def generate(self):
        screen_x = np.arange(SIDEBAR_WIDTH, WINDOW_WIDTH - SIDEBAR_WIDTH, self.grid_spacing_px)
        screen_y = np.arange(0, WINDOW_HEIGHT, self.grid_spacing_px)
        SX, SY = np.meshgrid(screen_x, screen_y)

        # Convert screen to world coordinates
        X, Y = self.camera.screen_to_world(SX, SY)
        
        U = np.zeros_like(X, dtype=float)
        V = np.zeros_like(Y, dtype=float)


        for obj in self.scene.objects:
            dx = X - obj.x
            dy = Y - obj.y
            distance = np.sqrt(dx**2 + dy**2)
            distance = np.clip(distance, obj.radius, None)

            accel = G * obj.mass / (distance**2)
            U -= accel * (dx / distance)
            V -= accel * (dy / distance)

        vector_magnitude = np.sqrt(U**2 + V**2)

        return SX, SY, U, V