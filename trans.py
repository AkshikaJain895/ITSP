import mediapipe as mp
from header2 import *

landmarks_list = []
whitekeys = []
blackkeys = []
midpoints = []
hover_mode = False
show = True

# initialise serial port
try:
    ser = serial.Serial(serial_port, 9600)
except serial.SerialException as e:
    print(f"Error opening serial port {serial_port}: {e}")
    exit(1)

outport = mido.open_output('IAC Driver Bus 1')
print("MIDI Output opened successfully.")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

cv2.namedWindow('Live Feed')

ret, frame = cap.read()
if not ret:
    print("Error: Failed to capture image")
    exit()

h, w, _ = frame.shape
center_of_screen = point(w / 2, h / 2, 0)
initialz = w * 90 / 67 * 0.8
points = [center_of_screen + point(int(- w / 2 * 0.8), int(- w / 2 * 0.8 * pianoproportion), initialz),
          center_of_screen + point(int(w / 2 * 0.8), int(- w / 2 * 0.8 * pianoproportion), initialz),
          center_of_screen + point(int(w / 2 * 0.8), int(w / 2 * 0.8 * pianoproportion), initialz),
          center_of_screen + point(int(- w / 2 * 0.8), int(w / 2 * 0.8 * pianoproportion), initialz)
          ]

# initialise white key coordinates
for i in range(1, 26):
    midpoints.append(point_at_parameter(points[0], points[1], i / 26))
for i in range(1, 26):
    midpoints.append(point_at_parameter(points[2], points[3], i / 26))

# create the white keys
whitekeys.append(key(copy.deepcopy(points[0]), copy.deepcopy(midpoints[0]), copy.deepcopy(midpoints[49]), copy.deepcopy(points[3]), copy.deepcopy(whitekeymidinotes[0])))
for i in range(24):
    whitekeys.append(key(copy.deepcopy(midpoints[i]), copy.deepcopy(midpoints[i + 1]), copy.deepcopy(midpoints[48 - i]), copy.deepcopy(midpoints[49 - i]), copy.deepcopy(whitekeymidinotes[i + 1])))
whitekeys.append(key(copy.deepcopy(midpoints[24]), copy.deepcopy(points[1]), copy.deepcopy(points[2]), copy.deepcopy(midpoints[25]), copy.deepcopy(whitekeymidinotes[25])))

# create the black keys and if there is black key on white key
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

while True:
    current_time = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image")
        break

    command = 'x'
    ser.write(command.encode('utf-8'))
    
    # frame = cv2.flip(frame, 0)
    frame = cv2.flip(frame, 1)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # get fsr data
    channel_data =[]
    for i in range(10):
        response = ser.readline().decode('utf-8').rstrip()   
        channel_data.append(response)      
    fsr_readings =[]
    for data in channel_data:
        fsr_readings.append(int(re.search(r': (\d+)$', data).group(1)))  
    for i in range(10):
        print(f"Channel {i}: {fsr_readings[i]}")

    # draw the keys
    if show:
        for somekey in whitekeys:
            somekey.draw(frame, center_of_screen,initialz)
        for somekey in blackkeys:
            somekey.draw(frame, center_of_screen,initialz)

    #make currently playing = previously playing
    for somekey in whitekeys:
        somekey.previouslyplaying = somekey.currentlyplaying
        somekey.currentlyplaying = False
    for somekey in blackkeys:
        somekey.previouslyplaying = somekey.currentlyplaying
        somekey.currentlyplaying = False     
    
    frame_landmarks = []    
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label          
            hand_landmarks_data = {"hand_label": hand_label, "landmarks": {}}

            # get fingertip location data, draw fingertip circles, and play keys
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

                fsr_index = (idx // 4 - 1) * (1 - is_left) + (4 - (idx//4 - 1) + 5) * is_left

                finger_colour = finger_colours[int(idx / 4 + 5 * is_left - 1)]
                cv2.circle(frame, (cx, cy), 5, finger_colour, cv2.FILLED)
                found = 0

                # play black keys
                for i in range(18):
                    if point_in_quad(point(cx, cy, 0),blackkeys[i].project(center_of_screen, initialz)):
                        pointtodraw = point_at_parameter(point_at_parameter(blackkeys[i].topleft, blackkeys[i].topright, 0.5), point_at_parameter(blackkeys[i].bottomleft, blackkeys[i].bottomright, 0.5), 10 / 13).project(center_of_screen, initialz).integer().tuple()

                        cv2.circle(frame, pointtodraw, keyplayedradius, finger_colour, cv2.FILLED)
                        if(fsr_readings[fsr_index] > fsr_threshold or hover_mode):             
                            blackkeys[i].play(outport)
                            print("Sent the midi note")
                        
                        found = 1
                        break
                
                #play white keys
                if (not found):
                    for i in range(26):
                        if point_in_quad(point(cx, cy, 0),whitekeys[i].project(center_of_screen, initialz)):
                            pointtodraw = point_at_parameter(point_at_parameter(whitekeys[i].topleft, whitekeys[i].topright, 0.5), point_at_parameter(whitekeys[i].bottomleft, whitekeys[i].bottomright, 0.5), 10.5 / 13).project(center_of_screen, initialz).integer().tuple()
                            cv2.circle(frame, pointtodraw, keyplayedradius, finger_colour, cv2.FILLED)
                            if(fsr_readings[fsr_index] > fsr_threshold or hover_mode):
                                whitekeys[i].play(outport)
                                print("Sent the midi note")
                            break
            
            # stop keys which are not being played
            for somekey in whitekeys:
                if (somekey.previouslyplaying and not somekey.currentlyplaying):
                    somekey.stop(outport)
            for somekey in blackkeys:
                if (somekey.previouslyplaying and not somekey.currentlyplaying):
                    somekey.stop(outport)

            frame_landmarks.append(hand_landmarks_data)
    
    #if no hands on screen, stop all keys
    else:
        if (len(whitekeys) > 0):
            for somekey in whitekeys:
                somekey.stop(outport)
            for somekey in blackkeys:
                somekey.stop(outport)

    fps = 1 / (time.time() - current_time)
    cv2.putText(frame, f"FPS: {fps:0.1f}", (int(w * 0.1 * 0.75), int(h * 0.1)), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (50, 50, 50), 3, cv2.LINE_AA)
    cv2.putText(frame, f"Hover Mode: {hover_mode}", (int(w * 0.1 * 0.75), int(h * 0.15)), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (50, 50, 50), 3, cv2.LINE_AA)
    if (show):
        cv2.imshow('Live Feed', frame)

    # key presses
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
    if keypressed == ord('z'):
        hover_mode = not hover_mode


cap.release()
cv2.destroyAllWindows()
