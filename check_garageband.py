import mido
import time
from mido import MidiFile

def main():
    try:
        outport = mido.open_output('IAC Driver Bus 1')
        outport.send(mido.Message('note_on', note=60, velocity=100))
        outport.send(mido.Message('note_on', note=68, velocity=100))
        print("MIDI message sent successfully.")
        time.sleep(0.5)
        outport.send(mido.Message('note_off', note=60, velocity=100))
        
        outport.send(mido.Message('note_on', note=61, velocity=100))
        print("MIDI message sent successfully.")
        time.sleep(0.5)
        outport.send(mido.Message('note_off', note=61, velocity=100))
        outport.send(mido.Message('note_off', note=68, velocity=100))        
        outport.send(mido.Message('note_on', note=63, velocity=100))
        print("MIDI message sent successfully.")
        time.sleep(0.5)
        outport.send(mido.Message('note_off', note=63, velocity=100))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

