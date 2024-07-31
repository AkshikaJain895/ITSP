import time
import serial
import mido
from mido import Message

serial_port = '/dev/cu.usbmodem1101'  # Update this to your actual port

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
        sensor_line = ser.readline().strip().decode('utf-8')
        print(f"Received line: {sensor_line}")  # Debug print
        if sensor_line.startswith("Channel 4:"):
            try:
                sensor_value = int(sensor_line.split(":")[1].strip())
                print(f"Channel 4 sensor value: {sensor_value}")  # Debug print
                # Map sensor value (0-4095) to velocity (0-127)
                velocity = int(sensor_value / 4095.0 * 127)
                note = 60  # Middle C
                if velocity > 0:
                    send_midi_note_on(note, velocity)
                else:
                    send_midi_note_off(note)
            except ValueError:
                print(f"Invalid sensor value: {sensor_line}")  # Debug print

