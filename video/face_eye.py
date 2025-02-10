# import cv2
# import numpy as np

# # Initialize capture
# cap = cv2.VideoCapture(0)  # Use 0 for default webcam
# cap.set(3, 640)  # Width
# cap.set(4, 480)  # Height

# # Load cascade classifiers
# face_cascade = cv2.CascadeClassifier('D:/FYP/video/haarcascade_frontalface_default.xml')
# eye_cascade = cv2.CascadeClassifier('D:/FYP/video/haarcascade_eye.xml')

# while True:
#     # Capture frame-by-frame
#     ret, frame = cap.read()
    
#     # Our operations on the frame come here
#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
#     # Detect faces
#     faces = face_cascade.detectMultiScale(frame, 1.3, 5)
    
#     # Draw rectangles around detected faces
#     for (x,y,w,h) in faces:
#         cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
#         roi_gray = frame[y:y+h, x:x+w]
#         roi_color = frame[y:y+h, x:x+w]
        
#         # Detect eyes within face region
#         eyes = eye_cascade.detectMultiScale(roi_gray)
#         for (ex,ey,ew,eh) in eyes:
#             cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
    
#     # Display the resulting frame
#     cv2.imshow('frame', frame)
    
#     # Break the loop on 'q' press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()




#NEw code 

# import cv2
# import numpy as np

# # Initialize capture
# cap = cv2.VideoCapture(0)  # Use 0 for default webcam
# cap.set(3, 640)  # Width
# cap.set(4, 480)  # Height

# # Load cascade classifiers
# face_cascade = cv2.CascadeClassifier('D:/FYP/video/haarcascade_frontalface_default.xml')
# eye_cascade = cv2.CascadeClassifier('D:/FYP/video/haarcascade_eye.xml')

# while True:
#     # Capture frame-by-frame
#     ret, frame = cap.read()
    
#     if not ret:
#         print("Failed to grab frame")
#         break
        
#     # Convert to grayscale for detection
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
#     # Detect faces in grayscale image
#     faces = face_cascade.detectMultiScale(
#         gray,
#         scaleFactor=1.3,
#         minNeighbors=5,
#         minSize=(30, 30)
#     )
    
#     # Draw rectangles around detected faces on color frame
#     for (x, y, w, h) in faces:
#         # Draw blue rectangle for face
#         cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
        
#         # Create ROI for eyes
#         roi_gray = gray[y:y+h, x:x+w]
#         roi_color = frame[y:y+h, x:x+w]
        
#         # Detect eyes within face region
#         eyes = eye_cascade.detectMultiScale(
#             roi_gray,
#             scaleFactor=1.1,
#             minNeighbors=5,
#             minSize=(20, 20)
#         )
        
#         # Draw green rectangles for eyes
#         for (ex, ey, ew, eh) in eyes:
#             cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
    
#     # Display the resulting frame
#     cv2.imshow('Face and Eye Detection', frame)
    
#     # Break the loop on 'q' press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()



# NEw code -3 
import cv2
import numpy as np

# Initialize capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load cascade classifiers
face_cascade = cv2.CascadeClassifier('D:/FYP/video/haarcascade_frontalface_default.xml')
# Try the alternative eye cascade which sometimes works better
eye_cascade = cv2.CascadeClassifier('D:/FYP/video/haarcascade_eye.xml')

# Check if cascades are loaded correctly
if face_cascade.empty():
    raise IOError('Unable to load face cascade classifier xml file')
if eye_cascade.empty():
    raise IOError('Unable to load eye cascade classifier xml file')

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
        
    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Enhance contrast of the grayscale image
    gray = cv2.equalizeHist(gray)
    
    # Detect faces in grayscale image
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
        
        # Create ROI for eyes - only use upper half of face
        roi_gray = gray[y:y+h//2, x:x+w]    # Only upper half of face
        roi_color = frame[y:y+h//2, x:x+w]
        
        # Improve contrast in eye region
        roi_gray = cv2.equalizeHist(roi_gray)
        
        # More lenient parameters for eye detection
        eyes = eye_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.05,      # Smaller scale factor for more detections
            minNeighbors=6,        # Increased for more reliable detections
            minSize=(25, 25),      # Minimum size for an eye
            maxSize=(45, 45)       # Maximum size for an eye
        )
        
        for (ex, ey, ew, eh) in eyes:
            # Draw both rectangle and circle for better visualization
            cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
            center = (ex + ew//2, ey + eh//2)
            radius = min(ew//2, eh//2)
            cv2.circle(roi_color, center, radius, (0,0,255), 2)
    
    cv2.imshow('Face and Eye Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()