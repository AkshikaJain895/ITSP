import cv2
import mediapipe as mp
import time

# Initialize MediaPipe Hands.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# Initialize MediaPipe drawing utility.
mp_drawing = mp.solutions.drawing_utils

# Open the webcam.
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1000)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)


# Define landmark labels.
landmark_labels = [
    'WRIST',
    'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP',
    'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP', 'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP',
    'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP', 'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP',
    'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP', 'RING_FINGER_TIP',
    'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP'
]

# Fingertip indices.
fingertip_indices = [4, 8, 12, 16, 20]

# List to store landmarks and timestamps.
landmarks_list = []

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Get current time.
    current_time = time.time()

    #flip the image
    #image = cv2.flip(image, 1)

    # Convert the BGR image to RGB.
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find hands.
    results = hands.process(image_rgb)

    # Store and draw only fingertip landmarks and print their labels.
    frame_landmarks = []
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Get the handedness label ('Left' or 'Right')
            hand_label = handedness.classification[0].label
            print(f"Detected {hand_label} hand")
            
            hand_landmarks_data = {"hand_label": hand_label, "landmarks": {}}
            for idx in fingertip_indices:
                landmark = hand_landmarks.landmark[idx]
                # Print landmark coordinates and label.
                #print(f"Landmark {landmark_labels[idx]} ({hand_label} hand): (x={landmark.x}, y={landmark.y}, z={landmark.z})")
                
                # Store the landmark in the hand_landmarks_data dictionary.
                hand_landmarks_data["landmarks"][landmark_labels[idx]] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z
                }
                
                # Draw only the fingertip landmarks.
                h, w, _ = image.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
                cv2.putText(image, f"{landmark_labels[idx]} ({hand_label})", (cx, cy), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            fps = 0
            if landmarks_list:
                fps = 1 / (current_time - landmarks_list[-1]["timestamp"])

            cv2.putText(image, f"FPS: {fps:0.1f}", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (50, 50, 50), 3, cv2.LINE_AA)

            # Add the hand landmarks data to the frame_landmarks list.
            frame_landmarks.append(hand_landmarks_data)

    # Add the current frame's landmarks and timestamp to landmarks_list.
    if frame_landmarks:
        landmarks_list.append({"timestamp": current_time, "frame_landmarks": frame_landmarks})

    # Remove elements older than 10 seconds.
    landmarks_list = [entry for entry in landmarks_list if current_time - entry["timestamp"] <= 10]

    # Display the image.
    cv2.imshow('MediaPipe Hands', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()

# Print out the stored landmarks.

for entry in landmarks_list:
    print(f"Timestamp: {entry['timestamp']}")
    for hand_data in entry['frame_landmarks']:
        print(f"  {hand_data['hand_label']} hand:")
        for tip, coords in hand_data['landmarks'].items():
            print(f"    {tip}: (x={coords['x']}, y={coords['y']}, z={coords['z']})")

print(f"Length of list: {len(landmarks_list)}\nAverage fps = {len(landmarks_list)/10}")

