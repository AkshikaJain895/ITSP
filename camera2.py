import cv2
import numpy as np

def detect_piano_keys(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding to highlight the keys
    adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Detect edges using Canny edge detector
    edges = cv2.Canny(adaptive_thresh, 50, 150)

    # Find contours of the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    key_positions = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if 0.1 < aspect_ratio < 1.0 and w > 20 and h > 40:  # Filter out small contours and non-key shapes
            key_positions.append((x, x + w))
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(image, f'({x}, {y})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

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

    # Define the region of interest (ROI) where the piano keys are likely to be
    height, width = frame.shape[:2]
    roi = frame[int(height * 0.25):int(height * 0.75), int(width * 0.1):int(width * 0.9)]

    key_positions = detect_piano_keys(roi)

    # Draw the ROI rectangle for visualization
    cv2.rectangle(frame, (int(width * 0.1), int(height * 0.25)), (int(width * 0.9), int(height * 0.75)), (0, 255, 0), 2)

    cv2.imshow('Webcam Feed with Keys', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

