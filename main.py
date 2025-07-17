import pygame
import importlib
import gravity_simulator_2  # Import your simulation file
import time
import os

# Constants
FPS = 60
RELOAD_CHECK_INTERVAL = 0.5  # Check for updates every 0.5 seconds

# Track the last modification time of the simulation file
simulation_file = "gravity_simulator_2.py"
last_modified_time = os.path.getmtime(simulation_file)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((gravity_simulator_2.WIDTH, gravity_simulator_2.HEIGHT))
pygame.display.set_caption("Dynamic Vector Field Simulation")
clock = pygame.time.Clock()

running = True
while running:
    # Check for updates to the simulation file
    current_modified_time = os.path.getmtime(simulation_file)
    if current_modified_time != last_modified_time:
        print("Detected changes in simulation.py. Reloading...")
        importlib.reload(gravity_simulator_2)
        last_modified_time = current_modified_time

    # Run the simulation loop
    gravity_simulator_2.screen = screen  # Pass the main screen to the simulation
    gravity_simulator_2.running = running
    gravity_simulator_2.main_loop()  # Call the main loop from the simulation

    # Exit if the simulation sets running to False
    if not gravity_simulator_2.running:
        running = False

    # Delay to avoid frequent reload checks
    time.sleep(RELOAD_CHECK_INTERVAL)

pygame.quit()
