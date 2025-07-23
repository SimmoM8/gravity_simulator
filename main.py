import pygame
from gravity_simulator_2 import App
from config import WINDOW_WIDTH, WINDOW_HEIGHT

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dynamic Vector Field Simulation")

# Run the application
if __name__ == "__main__":
    app = App()
    app.run()

pygame.quit()
