"""
import cv2
import face_recognition

# showing image
img = cv2.imread("face_images/AliSamani.jpg")
# converting to rgb and encoding
rgb_img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
img_encoding = face_recognition.face_encodings(rgb_img)[0]

# showing image
img2 = cv2.imread("face_images/AliSamani2.jpg")
# converting to rgb and encoding
rgb_img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2RGB)
img_encoding2 = face_recognition.face_encodings(rgb_img2)[0]

# comparing two images
result = face_recognition.compare_faces([img_encoding], img_encoding2)
print("Result: ",result)

# show
cv2.imshow("img",img)
cv2.imshow("img 2",img2)
cv2.waitKey(0)
"""

import cv2
import faceRecognition

# Encode faces from folder
sfr = faceRecognition.SimpleFacerec()
sfr.load_encoding_images("face_images/")
# load camera
cap = cv2.VideoCapture(0)



while True:
    ret, frame = cap.read()

    # Detect faces
    face_location, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_location, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)
        cv2.rectangle(frame, (x1, y1),(x2, y2), (0,200,0),2)

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(3)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()