import pygame
import pygame.midi
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.midi.init()

# List available MIDI devices
print("Available MIDI devices:")
for i in range(pygame.midi.get_count()):
    info = pygame.midi.get_device_info(i)
    print(f"ID: {i}, Interface: {info[0]}, Name: {info[1]}, Input: {info[2]}, Output: {info[3]}")

# Choose the valid MIDI output device ID for IAC Driver
midi_out_id = 1  # Set to the output ID you identified

# Set up MIDI output
midi_out = pygame.midi.Output(midi_out_id)
midi_out.set_instrument(0)  # Set instrument to Acoustic Grand Piano

# Define the MIDI note for middle C (C4)
MIDDLE_C = 60

def play_note():
    midi_out.note_on(MIDDLE_C, 127)  # Play middle C with maximum velocity
    pygame.time.wait(10000)  # Wait for 500 milliseconds
    midi_out.note_off(MIDDLE_C, 127)  # Turn off the note

# Set up the main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_a:  # If the 'a' key is pressed
                play_note()
    
    # Limit the loop to 30 frames per second
    pygame.time.Clock().tick(30)

# Clean up and quit
midi_out.close()
pygame.midi.quit()
pygame.quit()

