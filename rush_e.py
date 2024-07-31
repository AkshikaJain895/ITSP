import mido
import time

def play_note_sequence(outport, notes, duration):
    for note_group in notes:
        # Send note_on for all notes in the group
        for note in note_group:
            outport.send(mido.Message('note_on', note=note, velocity=100))
        time.sleep(duration)
        # Send note_off for all notes in the group
        for note in note_group:
            outport.send(mido.Message('note_off', note=note, velocity=100))

def main():
    try:
        outport = mido.open_output('IAC Driver Bus 1')
        print("MIDI Output opened successfully.")
        
        # Simplified notes for "Rush E" melody and chords
        rush_e_notes = [
            (64,), (65,), (67,), (69,), (67,), (65,), (64,), (62,), (60,), (62,), (64,), (65,),
            (60, 64), (65, 69), (67, 71), (69, 72)  # Example chords
        ]
        
        # Duration for each note (in seconds)
        note_duration = 0.3
        
        play_note_sequence(outport, rush_e_notes, note_duration)
        
        print("MIDI message sent successfully.")
        
        outport.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

