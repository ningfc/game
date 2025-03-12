import pygame
import sys
import math

# Initialize Pygame
pygame.init()

RED = (255,0,0,0)

# Set up the display
width, height = pygame.display.Info().current_w * 0.9, pygame.display.Info().current_h * 0.8
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Image Translation Animation")

# Load the image
image = pygame.image.load("image/desktop.png")  # Replace with your image path
image_rect = image.get_rect()

angle = 0           # initial angle for elliptical motion
radius_x = (width - image_rect.width) / 2   # horizontal radius based on window width
radius_y = (height - image_rect.height) / 2   # vertical radius based on window height
center_x, center_y = width // 2, height // 2

pygame.font.init()
font = pygame.font.Font(None, 24)

# Main game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update elliptical movement
    angle += 0.05  # adjust rotation speed as needed
    x = center_x + radius_x * math.cos(angle) - image_rect.width / 2
    y = center_y + radius_y * math.sin(angle) - image_rect.height / 2

    # Clear the screen
    screen.fill((255, 255, 255))  # White background

    # Draw the image at its new position
    screen.blit(image, (x, y))

    surface = font.render(f'FPS:{int(clock.get_fps())}', True, RED)
    screen.blit(surface, (10,10))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
