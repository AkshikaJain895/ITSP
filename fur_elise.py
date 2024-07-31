import mido
import time

def play_note_sequence(outport, notes, duration):
    for note in notes:
        outport.send(mido.Message('note_on', note=note, velocity=100))
        time.sleep(duration)
        outport.send(mido.Message('note_off', note=note, velocity=100))

def main():
    try:
        outport = mido.open_output('IAC Driver Bus 1')
        print("MIDI Output opened successfully.")
        
        # Notes for "Für Elise" main theme
        fur_elise_notes = [
            76, 75, 76, 75, 76, 71, 74, 72, 69,
            60, 64, 69, 71,
            64, 68, 71, 72,
            64, 76, 75, 76, 75, 76, 71, 74, 72, 69
        ]
        
        # Duration for each note (in seconds)
        note_duration = 0.3
        
        play_note_sequence(outport, fur_elise_notes, note_duration)
        
        print("MIDI message sent successfully.")
        
        outport.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

