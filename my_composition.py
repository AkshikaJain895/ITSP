import mido
import time
import random

def play_note_sequence(outport, notes, base_duration):
    for note_group in notes:
        duration = base_duration * random.uniform(0.8, 1.2)  # Vary duration slightly
        velocities = [random.randint(50, 127) for _ in note_group]  # Random velocities for each note

        # Send note_on for all notes in the group with varying velocities
        for note, velocity in zip(note_group, velocities):
            outport.send(mido.Message('note_on', note=note, velocity=velocity))
        time.sleep(duration)
        # Send note_off for all notes in the group
        for note in note_group:
            outport.send(mido.Message('note_off', note=note, velocity=0))

def main():
    try:
        outport = mido.open_output('IAC Driver Bus 1')
        print("MIDI Output opened successfully.")
        
        # Example notes and chords
        notes_sequence = [
            (60,), (62,), (64,), (65,), (67,), (69,), (71,), (72,),  # Simple ascending scale
            (60, 64, 67), (62, 65, 69), (64, 67, 71), (65, 69, 72)  # Chords
        ]
        
        # Base duration for each note (in seconds)
        base_duration = 0.4
        
        # Play the note sequence with varying loudness and rhythm
        play_note_sequence(outport, notes_sequence, base_duration)
        
        print("MIDI message sent successfully.")
        
        outport.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

