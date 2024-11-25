import pygame

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

# Check for joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected!")
    pygame.quit()
    exit()

# Use the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick connected: {joystick.get_name()}")

# Main loop
try:
    while True:
        pygame.event.pump()  # Process events

        # Print axis values
        for i in range(joystick.get_numaxes()):
            print(f"Axis {i}: {joystick.get_axis(i):.3f}", end="  ")

        print("\r", end="")  # Stay on the same line

except KeyboardInterrupt:
    print("\nExiting...")
    pygame.quit()
