import mido
import time
import keyboard

# Function to send a different MIDI note
def send_different_note():
    try:
        outport = mido.open_output('IAC Driver Bus 1')
        outport.send(mido.Message('note_on', note=64, velocity=100))
        print("Different note on message sent successfully.")
        time.sleep(1)  # Keep the note on for 1 second
        outport.send(mido.Message('note_off', note=64, velocity=100))
        print("Different note off message sent successfully.")
        outport.close()
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    try:
	if not(keyboard.is_pressed('q')):
        	outport = mido.open_output('IAC Driver Bus 1')
        	print("MIDI Output opened successfully.")
        	outport.send(mido.Message('note_on', note=60, velocity=100))
        	print("Note on message sent successfully.")

        # Setting up the keyboard interrupt handler for alphabet keys
        #for char in 'abcdefghijklmnopqrstuvwxyz':
         #   keyboard.add_hotkey(char, send_different_note)

        # Keep the note on for a longer period, waiting for key press
        #print("Press any alphabet key to send a different MIDI note. Press 'Esc' to exit.")
        #keyboard.wait('esc')

        # Send note off for the original note
	else:
		outport = mido.open_output('IAC Driver Bus 1')
                print("MIDI Output opened successfully.")
                outport.send(mido.Message('note_on', note=60, velocity=100))
                print("Note on message sent successfully.")
        #outport.send(mido.Message('note_off', note=60, velocity=100))
        #print("Note off message sent successfully.")
        #outport.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

