from setup.config import (WINDOW_WIDTH, WINDOW_HEIGHT)

class Camera:
    def __init__(self, x_offset=0, y_offset=0, zoom=1, base_pixels_per_meter=0.00001):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.zoom = zoom
        self.base_pixels_per_meter = base_pixels_per_meter

    @property
    def pixels_per_meter(self):
        return self.base_pixels_per_meter * self.zoom

    def world_to_screen(self, wx, wy):
        sx = wx * self.pixels_per_meter + self.x_offset
        sy = wy * self.pixels_per_meter + self.y_offset
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = (sx - self.x_offset) / self.pixels_per_meter
        wy = (sy - self.y_offset) / self.pixels_per_meter
        return wx, wy

    def center_on(self, wx, wy):
        """Center the camera on a world coordinate."""
        self.x_offset = -wx * self.pixels_per_meter + (WINDOW_WIDTH // 2)
        self.y_offset = -wy * self.pixels_per_meter + (WINDOW_HEIGHT // 2)

    def zoom_around_point(self, zoom_in, anchor_screen_pos, factor=1.1):
        """Zoom in or out while keeping the anchor_screen_pos (x, y) fixed on screen."""
        ax, ay = anchor_screen_pos
        before_zoom = self.screen_to_world(ax, ay)

        if zoom_in:
            self.zoom *= factor
        else:
            self.zoom /= factor

        after_zoom = self.screen_to_world(ax, ay)

        dx = (after_zoom[0] - before_zoom[0]) * self.pixels_per_meter
        dy = (after_zoom[1] - before_zoom[1]) * self.pixels_per_meter

        self.x_offset += dx
        self.y_offset += dy

    def pan(self, dx_pixels, dy_pixels):
        """
        Move the camera by a given pixel amount, converted to world offsets.
        """
        self.x_offset += dx_pixels
        self.y_offset += dy_pixels

    def reset(self):
        """Reset camera to default position and zoom."""
        self.x_offset = 0
        self.y_offset = 0
        self.zoom = 1
        self.base_pixels_per_meter = 0.00001