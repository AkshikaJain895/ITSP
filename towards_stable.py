import cv2
import numpy as np
import mediapipe as mp
import threading
import time

# Initialize MediaPipe Hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Variables for threading
frame = None
thread_lock = threading.Lock()
stop_thread = False

# Initialize lists for smoothing
previous_positions = []
smoothing_factor = 5

def capture_frames():
    global frame, stop_thread
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open the webcam.")
        return

    while not stop_thread:
        ret, new_frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from the webcam.")
            break

        with thread_lock:
            frame = new_frame

    cap.release()

def detect_piano_keys(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image to highlight black keys
    inverted_gray = cv2.bitwise_not(gray)

    # Apply GaussianBlur to reduce noise and improve edge detection
    blurred_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    blurred_inverted = cv2.GaussianBlur(inverted_gray, (5, 5), 0)

    # Use adaptive thresholding to highlight the keys
    adaptive_thresh_gray = cv2.adaptiveThreshold(blurred_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    adaptive_thresh_inverted = cv2.adaptiveThreshold(blurred_inverted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Detect edges using Canny edge detector
    edges_gray = cv2.Canny(adaptive_thresh_gray, 50, 150)
    edges_inverted = cv2.Canny(adaptive_thresh_inverted, 50, 150)

    # Combine edges
    edges = cv2.bitwise_or(edges_gray, edges_inverted)

    # Find contours of the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    key_positions = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if 0.1 < aspect_ratio < 1.0 and w > 10 and h > 20:  # Filter out small contours and non-key shapes
            key_positions.append((x, y, w, h))
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(image, f'({x}, {y})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

    key_positions.sort()
    return key_positions

def smooth_positions(positions):
    if not positions:
        return None
    
    if len(previous_positions) < smoothing_factor:
        previous_positions.append(positions)
        return positions
    else:
        previous_positions.pop(0)
        previous_positions.append(positions)

    avg_positions = np.mean(previous_positions, axis=0).astype(int)
    return avg_positions

def detect_hands(image):
    # Convert the image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get coordinates of the index finger tip (landmark 8)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, _ = image.shape
            cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            smoothed_positions = smooth_positions((cx, cy))
            if smoothed_positions is not None:
                cv2.circle(image, tuple(smoothed_positions), 10, (0, 255, 0), -1)

    return image

def main():
    global frame, stop_thread
    threading.Thread(target=capture_frames).start()

    fps_time = time.time()
    while True:
        with thread_lock:
            if frame is None:
                continue
            frame_copy = frame.copy()

        # Resize frame for faster processing
        frame_resized = cv2.resize(frame_copy, (640, 480))

        # Define the region of interest (ROI) where the piano keys are likely to be
        height, width = frame_resized.shape[:2]
        roi = frame_resized[int(height * 0.5):, int(width * 0.1):int(width * 0.9)]

        key_positions = detect_piano_keys(roi)

        # Overlay the detected key positions back onto the original frame
        for (x, y, w, h) in key_positions:
            x1, y1 = x + int(width * 0.1), y + int(height * 0.5)
            cv2.rectangle(frame_resized, (x1, y1), (x1 + w, y1 + h), (255, 0, 0), 2)
            cv2.putText(frame_resized, f'({x1}, {y1})', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

        # Detect and draw hands
        frame_resized = detect_hands(frame_resized)

        # Calculate and display FPS
        fps = 1 / (time.time() - fps_time)
        fps_time = time.time()
        cv2.putText(frame_resized, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow('Webcam Feed with Keys and Hands', frame_resized)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_thread = True
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

