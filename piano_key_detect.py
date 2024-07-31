import cv2
import numpy as np

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

def number_keys(frame, keys_contours):
    # Sort contours from left to right
    bounding_boxes = [cv2.boundingRect(c) for c in keys_contours]
    (keys_contours, bounding_boxes) = zip(*sorted(zip(keys_contours, bounding_boxes),
                                                  key=lambda b: b[1][0], reverse=False))
    
    # Number the keys
    for i, cnt in enumerate(keys_contours):
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.putText(frame, str(i + 1), (x + w // 2, y + h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    return frame

def main():
    # Open a connection to the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture image.")
            break

        # Detect the keys
        keys_contours = detect_keys(frame)

        # Number the keys
        numbered_frame = number_keys(frame, keys_contours)

        # Display the resulting frame
        cv2.imshow('Numbered Piano Mat', numbered_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

