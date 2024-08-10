import mediapipe as mp
from header2 import *
import copy
import serial 
from mido import Message
import threading 

serial_port = '/dev/tty.usbmodem101' 
try:
    ser = serial.Serial(serial_port, 9600, timeout=0)
    print("Opened serial port ", serial_port)
except serial.SerialException as e:
    print(f"Error opening serial port {serial_port}: {e}")
    exit(1)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

blackkeypproportions = [(1, 28.5, 2, 6), (2, 34.1, 3, 12.9), (3, 41.1, 4, 20.3), (5, 32.5, 6, 11.5), (6, 35.5, 7, 14.5), (8, 28.5, 9, 6), (9, 34.1, 10, 12.9), (10, 41.1, 11, 20.3), (12, 32.5, 13, 11.5), (13, 35.5, 14, 14.5), (15, 28.5, 16, 6), (16, 34.1, 17, 12.9), (17, 41.1, 18, 20.3), (19, 32.5, 20, 11.5), (20, 35.5, 21, 14.5), (22, 28.5, 23, 6), (23, 34.1, 24, 12.9), (24, 41.1, 25, 20.3)]


if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

landmark_labels = [
    'WRIST',
    'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP',
    'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP', 'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP',
    'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP', 'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP',
    'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP', 'RING_FINGER_TIP',
    'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP'
]

fingertip_indices = [4, 8, 12, 16, 20]
landmarks_list = []

cv2.namedWindow('Live Feed')

whitekeys = []
whitekeymidinotes = [41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]
blackkeymidinotes = [42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78, 80, 82]
blackkeys = []
midpoints = []
finger_colours = [(0, 255, 255), (255, 255, 0), (255, 0, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 255), (255, 128, 0), (0, 255, 128), (128, 0, 255)]
moveunit = 2
rotateunit = 0.25
keyplayedradius = 10
show = True

outport = mido.open_output('IAC Driver Bus 1')
print("MIDI Output opened successfully.")

ret, frame = cap.read()
if not ret:
    print("Error: Failed to capture image")
    exit()

h, w, _ = frame.shape
center_of_screen = point(w / 2, h / 2, 0)
pianoproportion = 260 / 1222
initialz = w * 90 / 67 * 0.8
points = [center_of_screen + point(int(- w / 2 * 0.8), int(- w / 2 * 0.8 * pianoproportion), initialz),
          center_of_screen + point(int(w / 2 * 0.8), int(- w / 2 * 0.8 * pianoproportion), initialz),
          center_of_screen + point(int(w / 2 * 0.8), int(w / 2 * 0.8 * pianoproportion), initialz),
          center_of_screen + point(int(- w / 2 * 0.8), int(w / 2 * 0.8 * pianoproportion), initialz)
          ]

for i in range(1, 26):
    midpoints.append(point_at_parameter(points[0], points[1], i / 26))
for i in range(1, 26):
    midpoints.append(point_at_parameter(points[2], points[3], i / 26))

whitekeys.append(key(copy.deepcopy(points[0]), copy.deepcopy(midpoints[0]), copy.deepcopy(midpoints[49]), copy.deepcopy(points[3]), copy.deepcopy(whitekeymidinotes[0])))
for i in range(24):
    whitekeys.append(key(copy.deepcopy(midpoints[i]), copy.deepcopy(midpoints[i + 1]), copy.deepcopy(midpoints[48 - i]), copy.deepcopy(midpoints[49 - i]), copy.deepcopy(whitekeymidinotes[i + 1])))
whitekeys.append(key(copy.deepcopy(midpoints[24]), copy.deepcopy(points[1]), copy.deepcopy(points[2]), copy.deepcopy(midpoints[25]), copy.deepcopy(whitekeymidinotes[25])))

currentblackkeynumber = 0
for keydata in blackkeypproportions:
    topleft = point_at_parameter(whitekeys[keydata[0] - 1].topleft, whitekeys[keydata[0] - 1].topright, keydata[1] / 44)
    topright = point_at_parameter(whitekeys[keydata[2] - 1].topleft, whitekeys[keydata[2] - 1].topright, keydata[3] / 44)
    bottomright = point_at_parameter(whitekeys[keydata[2] - 1].bottomleft, whitekeys[keydata[2] - 1].bottomright, keydata[3] / 44)
    bottomleft = point_at_parameter(whitekeys[keydata[0] - 1].bottomleft, whitekeys[keydata[0] - 1].bottomright, keydata[1] / 44)

    bottomright = point_at_parameter(topright, bottomright, 8 / 13)
    bottomleft = point_at_parameter(topleft, bottomleft, 8 / 13)
    blackkeys.append(key(topleft, topright, bottomright, bottomleft, blackkeymidinotes[currentblackkeynumber],type = 'black'))
    currentblackkeynumber += 1

for somekey in blackkeypproportions:
    whitekeys[somekey[0] - 1].blackkeyonright = True
    whitekeys[somekey[2] - 1].blackkeyonleft = True


ret, frame = cap.read()
if not ret:
    print("Error: Failed to capture image")
    exit()
sensor_value=0
while True:
    #ser.flushInput()
    #print("Flushed")
    if ser.in_waiting>0 :
        #ser.flushInput()
        sensor_value = ser.readline().strip()
        print("read sensor")
        try:
            sensor_value_str = sensor_value.decode('utf-8')
            #print(f"Decoded sensor value: {sensor_value_str}")  # Debug print

        # Extract the numerical part after the colon
            sensor_value = int(sensor_value_str.split(':')[-1].strip())
            
            print(sensor_value)
            ser.flushInput()
        except ValueError:
            print(f"Invalid sensor value {sensor_value}")

    current_time = time.time()
    ret, frame = cap.read()
    frame = cv2.flip(frame, 0)
    frame = cv2.flip(frame, 1)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    if show:
        for somekey in whitekeys:
            somekey.draw(frame, center_of_screen,initialz)
        for somekey in blackkeys:
            somekey.draw(frame, center_of_screen,initialz)
            

    results = hands.process(image_rgb)
    frame_landmarks = []
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Get the handedness label ('Left' or 'Right')
            hand_label = handedness.classification[0].label
            # print(f"Detected {hand_label} hand")
            
            hand_landmarks_data = {"hand_label": hand_label, "landmarks": {}}
            for somekey in whitekeys:
                somekey.previouslyplaying = somekey.currentlyplaying
                somekey.currentlyplaying = False
            for somekey in blackkeys:
                somekey.previouslyplaying = somekey.currentlyplaying
                somekey.currentlyplaying = False

            for idx in fingertip_indices:
                landmark = hand_landmarks.landmark[idx]
                hand_landmarks_data["landmarks"][landmark_labels[idx]] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z
                }
                h, w, _ = frame.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                is_left = 0
                if hand_label == 'Left':
                    is_left = 1

                finger_colour = finger_colours[int(idx / 4 + 5 * is_left - 1)]
                cv2.circle(frame, (cx, cy), 5, finger_colour, cv2.FILLED)
                found = 0
                for i in range(18):
                    if point_in_quad(point(cx, cy, 0),blackkeys[i].project(center_of_screen, initialz)):
                        pointtodraw = point_at_parameter(point_at_parameter(blackkeys[i].topleft, blackkeys[i].topright, 0.5), point_at_parameter(blackkeys[i].bottomleft, blackkeys[i].bottomright, 0.5), 10 / 13).project(center_of_screen, initialz).integer().tuple()

                        cv2.circle(frame, pointtodraw, keyplayedradius, finger_colour, cv2.FILLED)
                        if sensor_value>300 :
                            blackkeys[i].play(outport)
                            print("Played well")
                        
                        found = 1
                        break

                if (not found):
                    for i in range(26):
                        if point_in_quad(point(cx, cy, 0),whitekeys[i].project(center_of_screen, initialz)):
                            pointtodraw = point_at_parameter(point_at_parameter(whitekeys[i].topleft, whitekeys[i].topright, 0.5), point_at_parameter(whitekeys[i].bottomleft, whitekeys[i].bottomright, 0.5), 10.5 / 13).project(center_of_screen, initialz).integer().tuple()
                            cv2.circle(frame, pointtodraw, keyplayedradius, finger_colour, cv2.FILLED)
                            if sensor_value>300:
                                whitekeys[i].play(outport)
                                print("Played well again")
                            break
            for somekey in whitekeys:
                if (somekey.previouslyplaying and not somekey.currentlyplaying):
                    somekey.stop(outport)
            for somekey in blackkeys:
                if (somekey.previouslyplaying and not somekey.currentlyplaying):
                    somekey.stop(outport)

            frame_landmarks.append(hand_landmarks_data)
    else:
        if (len(whitekeys) > 0):
            for somekey in whitekeys:
                somekey.stop(outport)
            for somekey in blackkeys:
                somekey.stop(outport)

    fps = 1 / (time.time() - current_time)
    cv2.putText(frame, f"FPS: {fps:0.1f}", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (50, 50, 50), 3, cv2.LINE_AA)
    #print(fps)
    if (show):
        cv2.imshow('Live Feed', frame)

    keypressed = cv2.waitKey(1) & 0xFF
    if keypressed == ord('q'):
        break
   
    if keypressed == ord('w'):
        for somekey in whitekeys:
            somekey.move('y', -moveunit)
        for somekey in blackkeys:
            somekey.move('y', -moveunit)

    if keypressed == ord('s'):
        for somekey in whitekeys:
            somekey.move('y', moveunit)
        for somekey in blackkeys:
            somekey.move('y', moveunit)

    if keypressed == ord('a'):
        for somekey in whitekeys:
            somekey.move('x', -moveunit)
        for somekey in blackkeys:
            somekey.move('x', -moveunit)

    if keypressed == ord('d'):
        for somekey in whitekeys:
            somekey.move('x', moveunit)
        for somekey in blackkeys:
            somekey.move('x', moveunit)
    
    if keypressed == ord('t'):
        for somekey in whitekeys:
            somekey.move('z', moveunit)
        for somekey in blackkeys:
            somekey.move('z', moveunit)

    if keypressed == ord('g'):
        for somekey in whitekeys:
            somekey.move('z', -moveunit)
        for somekey in blackkeys:
            somekey.move('z', -moveunit)

    if keypressed == ord('u'):
        rotationcenter = center_of_keys(whitekeys)
        for somekey in whitekeys:
            somekey.rotate('z', rotationcenter, rotateunit)
        for somekey in blackkeys:
            somekey.rotate('z', rotationcenter, rotateunit)

    if keypressed == ord('i'):
        rotationcenter = center_of_keys(whitekeys)
        for somekey in whitekeys:
            somekey.rotate('z', rotationcenter, -rotateunit)
        for somekey in blackkeys:
            somekey.rotate('z', rotationcenter, -rotateunit)
    
    if keypressed == ord('y'):
        rotationcenter = center_of_keys(whitekeys)
        for somekey in whitekeys:
            somekey.rotate('x', rotationcenter, -rotateunit)
        for somekey in blackkeys:
            somekey.rotate('x', rotationcenter, -rotateunit)

    if keypressed == ord('h'):
        rotationcenter = center_of_keys(whitekeys)
        for somekey in whitekeys:
            somekey.rotate('x', rotationcenter, rotateunit)
        for somekey in blackkeys:
            somekey.rotate('x', rotationcenter, rotateunit)

    if keypressed == ord('j'):
        rotationcenter = center_of_keys(whitekeys)
        for somekey in whitekeys:
            somekey.rotate('y', rotationcenter, rotateunit)
        for somekey in blackkeys:
            somekey.rotate('y', rotationcenter, rotateunit)

    if keypressed == ord('k'):
        rotationcenter = center_of_keys(whitekeys)
        for somekey in whitekeys:
            somekey.rotate('y', rotationcenter, -rotateunit)
        for somekey in blackkeys:
            somekey.rotate('y', rotationcenter, -rotateunit)
    
    if keypressed == ord('r'):
        for somekey in whitekeys:
            somekey.reset_position()
        for somekey in blackkeys:
            somekey.reset_position()

    if keypressed == ord('x'):
        show = not show


cap.release()
cv2.destroyAllWindows()