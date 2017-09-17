import cv2
import detectPerson

# Capture video from camera
# -------------------------
videoCap = cv2.VideoCapture(2)

count = 1
while(True):
    # Capture frame-by-frame
    ret, frame = videoCap.read()
    # Detect person in frame and return direction the car should go in (Left, Right, or Forward)
    direction, isPersonStopping, coords = detectPerson.detect_person(frame)

    print(direction)
    
    # To quit video
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
videoCap.release()
cv2.destroyAllWindows()

print('\nProcess complete.\n')