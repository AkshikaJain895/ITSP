import cv2
import numpy as np

def detect_piano_keys(image):
    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for white keys in HSV
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])

    # Define the range for black keys in HSV
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])

    # Threshold the HSV image to get only the white keys
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    # Threshold the HSV image to get only the black keys
    black_mask = cv2.inRange(hsv, lower_black, upper_black)

    # Apply morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
    black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_CLOSE, kernel)
    black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_OPEN, kernel)

    # Find contours of the white keys
    white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    black_contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    key_positions = []

    for contour in white_contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 20 and h > 20:  # Filter out small contours that are not keys
            key_positions.append((x, x + w))
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(image, f'({x}, {y})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

    for contour in black_contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 10 and h > 40:  # Filter out small contours that are not keys
            key_positions.append((x, x + w))
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f'({x}, {y})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    key_positions.sort()
    return key_positions

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Unable to open the webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame from the webcam.")
        break

    frame = cv2.resize(frame, (1280, 720))
    key_positions = detect_piano_keys(frame)

    cv2.imshow('Webcam Feed with Keys', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

