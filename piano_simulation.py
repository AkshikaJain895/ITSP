import pygame
import time

# Initialize pygame mixer
pygame.mixer.init()

# Dictionary mapping key numbers to sound file paths
piano_sounds = {i: f'key{i}.wav' for i in range(1, 62)}

def play_piano_key(key_number):
    if key_number in piano_sounds:
        sound_file = piano_sounds[key_number]
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Wait for the sound to finish playing
            time.sleep(0.1)
    else:
        print("Invalid key number. Please choose a number from 1 to 61.")

# Main loop
while True:
    user_input = input("Enter the piano key number to play (1-61) or 'quit' to exit: ").strip()
    if user_input.lower() == 'quit':
        break
    try:
        key_number = int(user_input)
        play_piano_key(key_number)
    except ValueError:
        print("Invalid input. Please enter a number from 1 to 61 or 'quit' to exit.")

