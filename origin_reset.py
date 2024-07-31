import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def preprocess_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Gaussian blur to reduce noise and smooth the image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    return edges

def detect_keys(frame):
    # Preprocess the frame
    edges = preprocess_frame(frame)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out small contours that are not keys
    min_contour_area = 1000
    keys_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
    
    return keys_contours

# Open a connection to the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

first_key_origin = None

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Invert the frame vertically
    frame = cv2.flip(frame, 0)
    
    # Convert the BGR image to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and detect hands
    results = hands.process(frame_rgb)

    # Detect the keys
    keys_contours = detect_keys(frame)
    
    if keys_contours:
        # Sort contours from left to right
        bounding_boxes = [cv2.boundingRect(c) for c in keys_contours]
        (keys_contours, bounding_boxes) = zip(*sorted(zip(keys_contours, bounding_boxes), key=lambda b: b[1][0], reverse=False))

        # Get the coordinates of the first key
        x, y, w, h = bounding_boxes[0]

        # Set the origin to the beginning of the first key
        first_key_origin = (x, y)

        # Print the starting coordinates of the first key
        print(f"First Key Coordinates: x={x}, y={y}")

        # Draw a rectangle around the first key
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    if first_key_origin:
        ox, oy = first_key_origin
        
        # Draw hand landmarks relative to the new origin
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the coordinates of the forefinger tip (landmark 8)
                forefinger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, _ = frame.shape
                cx, cy = int(forefinger_tip.x * w) - ox, int(forefinger_tip.y * h) - oy

                # Print the coordinates relative to the new origin
                print(f"Forefinger Tip Coordinates (Relative): x={cx}, y={cy}")

                # Draw a circle at the forefinger tip relative to the new origin
                cv2.circle(frame, (cx + ox, cy + oy), 10, (0, 255, 0), -1)

    # Display the resulting frame
    cv2.imshow('MediaPipe Hands and Piano Mat Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()

