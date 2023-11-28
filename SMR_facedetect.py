import cv2

def detect_face_with_mask(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Try face detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        return True

    #if standard face detection fails, try another method (mask for example)
    for (x, y, w, h) in faces:
        roi = gray[y:y+h, x:x+w]
        mouth_rectangles = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_mouth.xml').detectMultiScale(roi)
        if len(mouth_rectangles) > 0:
            return True

    # Return False if no face or mask is detected
    return False

#Testing
image_path = './2.jpg'      #replace with actual image path
result = detect_face_with_mask(image_path)

if result:
    print("Face detected in the image.")
else:
    print("No face detected in the image.")
