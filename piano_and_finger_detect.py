import cv2
import mediapipe as mp

# Initialize MediaPipe Hands and drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define the piano keys mapping
# Assuming a simple linear mapping for the 44 keys
# This might need adjustments based on the exact dimensions and layout of the piano mat
KEY_WIDTH = 20  # Adjust this based on actual width of each key on the mat
KEYS = ["C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
        "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
        "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
        "C4", "C#4", "D4", "D#4"]

def get_key_from_position(x):
    # Assuming x is the x-coordinate of the fingertip
    # Map x to the corresponding key index
    key_index = int(x // KEY_WIDTH)
    if key_index < len(KEYS):
        return KEYS[key_index]
    else:
        return "Unknown Key"

def main():
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame and find hands
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Loop through index finger tips (landmark 8) to get x-coordinates
                    for id, lm in enumerate(hand_landmarks.landmark):
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        
                        if id == 8:  # Index finger tip
                            key_note = get_key_from_position(cx)
                            cv2.putText(frame, key_note, (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            print(f"Key Pressed: {key_note}")

            # Display the frame
            cv2.imshow('Piano Key Detector', frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
