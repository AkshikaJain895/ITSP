import pygame
import pygame.midi

# Initialize Pygame MIDI
pygame.midi.init()

# List available MIDI devices
print("Available MIDI devices:")
for i in range(pygame.midi.get_count()):
    info = pygame.midi.get_device_info(i)
    print(f"ID: {i}, Interface: {info[0]}, Name: {info[1]}, Input: {info[2]}, Output: {info[3]}")

# Shutdown Pygame MIDI
pygame.midi.quit()

