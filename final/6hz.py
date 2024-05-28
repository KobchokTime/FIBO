import pygame
import sys
import os
import time

# Set the position of the window
x, y = 1000, 300  # Coordinates for the top-left corner of the window
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

# Initialize pygame
pygame.init()

# Set screen dimensions
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black and White Swap")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set initial color
current_color = BLACK

# Set frequency (in Hz)
frequency = 12

# Calculate period in seconds
period_s = 1.0 / frequency

# Variables for calculating the real frequency
last_time = time.time()
swap_time = last_time
swap_count = 0

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the current time
    current_time = time.time()

    # Change color if the period has elapsed
    if current_time - swap_time >= period_s:
        current_color = WHITE if current_color == BLACK else BLACK
        swap_time = current_time
        swap_count += 1

        # Fill the screen with the current color
        screen.fill(current_color)

        # Update the display
        pygame.display.flip()

    # Calculate the real frequency every second
    if current_time - last_time >= 1.0:
        real_frequency = swap_count / (current_time - last_time)
        print(f"Real Frequency of 6 Hz: {real_frequency:.2f} Hz")
        last_time = current_time
        swap_count = 0

    # Cap the frame rate (comment out to prevent interference with timing)
    # clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
