import time
import serial
import mido
from mido import Message

# Replace with the correct serial port identified from the steps above
serial_port = '/dev/tty.usbmodem101'  # Update this

# Wait for a moment to ensure the port is available
time.sleep(2)

# Initialize serial port
try:
    ser = serial.Serial(serial_port, 9600)

except serial.SerialException as e:
    print(f"Error opening serial port {serial_port}: {e}")
    exit(1)

# Open MIDI output
try:
    midi_out = mido.open_output('IAC Driver Bus 1')  # Change to your IAC Driver bus name
except IOError as e:
    print(f"Error opening MIDI output: {e}")
    exit(1)

def send_midi_note_on(note, velocity):
    msg = Message('note_on', note=note, velocity=velocity)
    print(f"Sending MIDI Note On: {msg}")  # Debug print
    midi_out.send(msg)

def send_midi_note_off(note):
    msg = Message('note_off', note=note)
    print(f"Sending MIDI Note Off: {msg}")  # Debug print
    midi_out.send(msg)

print("Starting the loop...")

while True:
    if ser.in_waiting > 0:
        # Read sensor value from serial
        sensor_value = ser.readline().strip()
        #print(f"raw {sensor_value}")
        try:
            sensor_value_str = sensor_value.decode('utf-8')
            #print(f"Decoded sensor value: {sensor_value_str}")  # Debug print

        # Extract the numerical part after the colon
            sensor_value = int(sensor_value_str.split(':')[-1].strip())
            #print(f"Extracted sensor value: {sensor_value}")
            velocity = int(sensor_value / 4095.0 * 127)
            note = 60  # Middle C
            if velocity > 0:
                send_midi_note_on(note, velocity)
            else:
                send_midi_note_off(note)
        except ValueError:
            print(f"Invalid sensor value: {sensor_value}")  # Debug print

